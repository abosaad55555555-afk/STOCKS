import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


def ai_v3_fast(df, lookback=50):
    df = df.copy()

    df["Range"] = df["High"] - df["Low"]
    df["Body"] = (df["Close"] - df["Open"]).abs()
    df["BodyPct"] = df["Body"] / df["Range"].replace(0, np.nan)
    df["Dir"] = np.sign(df["Close"] - df["Open"])
    df["ATR"] = df["Range"].rolling(14).mean()
    df["ATR_Norm"] = df["Range"] / df["ATR"]
    df["Vol_Norm"] = df["Volume"] / df["Volume"].rolling(20).mean()

    features = df[["BodyPct", "Dir", "ATR_Norm", "Vol_Norm"]].fillna(0).values

    pred = np.zeros(len(df))

    for i in range(lookback, len(df)):
        window = features[i - lookback:i]
        cur = features[i]

        sim = 1 - np.mean(np.abs(window - cur), axis=1)
        sim = np.clip(sim, 0, 1)

        moves = df["Close"].values[i - lookback + 1:i + 1] - df["Open"].values[i - lookback + 1:i + 1]

        pred[i] = np.sum(sim * moves) / (np.sum(sim) + 1e-9)

    df["AI_PredMove"] = pred
    return df


def auto_tune(df):
    df = df.copy()
    df["Thr"] = df["AI_PredMove"].abs().rolling(100).std().fillna(0.01)
    return df


def backtest(df):
    df = df.copy()

    df["Signal"] = 0
    df.loc[df["AI_PredMove"] > df["Thr"], "Signal"] = 1
    df.loc[df["AI_PredMove"] < -df["Thr"], "Signal"] = -1

    df["Return"] = df["Close"].pct_change()
    df["Strategy"] = df["Signal"].shift(1) * df["Return"]
    df["Equity"] = (1 + df["Strategy"]).cumprod().fillna(1)

    return df


def performance(df):
    total_return = df["Equity"].iloc[-1] - 1
    win_rate = (df["Strategy"] > 0).mean()
    max_dd = (df["Equity"].cummax() - df["Equity"]).max()

    return {
        "Total Return %": round(total_return * 100, 2),
        "Win Rate %": round(win_rate * 100, 2),
        "Max Drawdown %": round(max_dd * 100, 2)
    }


def plot_equity(df):
    plt.plot(df.index, df["Equity"])
    plt.title("AI V3 FAST – Equity Curve")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    df = yf.download("MSFT", period="5y", interval="1d")
    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df = ai_v3_fast(df)
    df = auto_tune(df)
    df = backtest(df)

    print(performance(df))
    plot_equity(df)
