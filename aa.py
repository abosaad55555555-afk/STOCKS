# ================================
# AI V3 – PRO Python Engine
# Predict + Auto‑Tune + Backtest
# ================================

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


# ================================
# 1) AI‑V3 PRO: Neural Similarity + Regime + MTF
# ================================
def ai_v3_pro(df, lookback=300, decay=0.65):
    df = df.copy()

    df["Range"] = df["High"] - df["Low"]
    df["Body"] = (df["Close"] - df["Open"]).abs()
    df["BodyPct"] = df["Body"] / df["Range"].replace(0, np.nan)
    df["Dir"] = np.sign(df["Close"] - df["Open"])
    df["ATR"] = df["Range"].rolling(14).mean()
    df["ATR_Norm"] = df["Range"] / df["ATR"]
    df["Vol_Norm"] = df["Volume"] / df["Volume"].rolling(20).mean()

    # ============================
    # Regime Detection (Daily)
    # ============================
    close_series = df["Close"].astype(float)

    ma_trend = close_series.rolling(50).mean()
    if isinstance(ma_trend, pd.DataFrame):
        ma_trend = ma_trend.iloc[:, 0]
    ma_trend = ma_trend.reindex(df.index, method="ffill")

    df["MA_Trend"] = ma_trend
    df["Regime"] = np.where(close_series.values > ma_trend.values, 1, -1)

    # ============================
    # MTF Reinforcement (Weekly)
    # ============================
    weekly_ma = close_series.resample("W").last().rolling(10).mean()
    if isinstance(weekly_ma, pd.DataFrame):
        weekly_ma = weekly_ma.iloc[:, 0]
    weekly_ma = weekly_ma.reindex(df.index, method="ffill")

    df["MTF_MA"] = weekly_ma
    df["MTF_Signal"] = np.where(close_series.values > weekly_ma.values, 1, -1)

    preds = []

    # ============================
    # Neural Similarity Engine
    # ============================
    for i in range(len(df)):
        if i < lookback:
            preds.append(0.0)
            continue

        cur = df.iloc[i]
        cur_vec = np.array([
            cur["BodyPct"],
            cur["Dir"],
            cur["ATR_Norm"],
            cur["Vol_Norm"]
        ])

        sims = []
        moves = []

        for j in range(i - lookback, i):
            past = df.iloc[j]
            past_vec = np.array([
                past["BodyPct"],
                past["Dir"],
                past["ATR_Norm"],
                past["Vol_Norm"]
            ])

            dist = np.abs(cur_vec - past_vec)
            sim = 1 - np.nanmean(dist)
            sim = max(sim, 0.0)

            age = i - j
            sim *= decay ** (age / lookback)

            sims.append(sim)

            if j + 1 < len(df):
                move = df.iloc[j + 1]["Close"] - df.iloc[j + 1]["Open"]
            else:
                move = 0.0
            moves.append(move)

        sims = np.array(sims)
        moves = np.array(moves)

        pred = (sims * moves).sum() / sims.sum() if sims.sum() > 0 else 0.0

        pred *= (1 + 0.05 * df["Regime"].iloc[i])
        pred *= (1 + 0.05 * df["MTF_Signal"].iloc[i])

        preds.append(pred)

    df["AI_PredMove"] = preds
    return df


# ================================
# 2) Auto‑Tune thresholds
# ================================
def auto_tune(df, window=200):
    df = df.copy()

    df["PredAbs"] = df["AI_PredMove"].abs()
    vol = df["PredAbs"].rolling(window).std()

    k = 0.7
    df["Thr"] = (vol * k).fillna(vol.mean() * k if not np.isnan(vol.mean()) else 0.0)

    return df


# ================================
# 3) Backtest
# ================================
def backtest_pro(df):
    df = df.copy()

    df["Signal"] = 0
    df.loc[df["AI_PredMove"] > df["Thr"], "Signal"] = 1
    df.loc[df["AI_PredMove"] < -df["Thr"], "Signal"] = -1

    df["Return"] = df["Close"].pct_change()
    df["Strategy"] = df["Signal"].shift(1) * df["Return"]

    df["Equity"] = (1 + df["Strategy"]).cumprod().fillna(1.0)

    return df


# ================================
# 4) Performance metrics
# ================================
def performance(df):
    total_return = df["Equity"].iloc[-1] - 1
    win_rate = (df["Strategy"] > 0).mean()
    max_dd = (df["Equity"].cummax() - df["Equity"]).max()

    return {
        "Total Return %": round(total_return * 100, 2),
        "Win Rate %": round(win_rate * 100, 2),
        "Max Drawdown %": round(max_dd * 100, 2)
    }


# ================================
# 5) Plot equity curve
# ================================
def plot_equity(df, title="AI V3 – Equity Curve"):
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Equity"], label="Strategy Equity")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Equity (normalized)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ================================
# 6) Full example
# ================================
if __name__ == "__main__":
    ticker = "MSFT"
    df = yf.download(ticker, period="5y", interval="1d")

    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

    df = ai_v3_pro(df)
    df = auto_tune(df)
    df = backtest_pro(df)

    print(performance(df))
    plot_equity(df)
