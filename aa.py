import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI V3 PRO", layout="wide")


# ============================
# AI V3 FAST ENGINE
# ============================
def ai_v3_fast(df, lookback=50):
    df = df.copy()

    if len(df) <= lookback + 5:
        df["AI_PredMove"] = 0.0
        return df

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

        moves = (
            df["Close"].values[i - lookback + 1:i + 1]
            - df["Open"].values[i - lookback + 1:i + 1]
        )

        w_sum = np.sum(sim)
        pred[i] = np.sum(sim * moves) / (w_sum + 1e-9)

    df["AI_PredMove"] = pred * 5
    return df


# ============================
# AUTO‑TUNE
# ============================
def auto_tune(df, window=50):
    df = df.copy()
    df["PredAbs"] = df["AI_PredMove"].abs()
    vol = df["PredAbs"].rolling(window).std()

    thr = vol.fillna(vol.mean() if not np.isnan(vol.mean()) else 0.0001)
    thr = thr.replace(0, 0.0001)

    df["Thr"] = thr * 0.5
    return df


# ============================
# BACKTEST — PURE NUMPY (NO PANDAS INSERT)
# ============================
def backtest(df):
    df = df.copy()

    closes = df["Close"].to_numpy()
    pred = df["AI_PredMove"].to_numpy()
    thr = df["Thr"].to_numpy()

    n = len(df)

    # --- Trend (manual MA) ---
    trend = np.zeros(n)
    for i in range(n):
        start = max(0, i - 49)
        trend[i] = closes[start:i+1].mean()

    # --- TrendSignal ---
    trend_signal = np.where(closes > trend, 1, -1)

    # --- Signals ---
    signal = np.zeros(n)
    signal[pred > thr] = 1
    signal[pred < -thr] = -1

    signal = signal * trend_signal

    # fallback
    if np.sum(np.abs(signal)) == 0 and np.sum(np.abs(pred)) != 0:
        signal = np.sign(pred)

    # --- Strategy ---
    returns = np.concatenate([[0], np.diff(closes) / closes[:-1]])
    strategy = np.roll(signal, 1) * returns
    strategy[0] = 0

    equity = np.cumprod(1 + strategy)

    # merge back into df
    df["Trend"] = trend
    df["TrendSignal"] = trend_signal
    df["Signal"] = signal
    df["Return"] = returns
    df["Strategy"] = strategy
    df["Equity"] = equity

    return df


# ============================
# PERFORMANCE
# ============================
def performance(df):
    if "Equity" not in df or df["Equity"].dropna().empty:
        return {
            "Total Return %": 0,
            "Win Rate %": 0,
            "Max Drawdown %": 0,
            "Note": "No equity data / no trades generated."
        }

    total_return = df["Equity"].iloc[-1] - 1
    win_rate = (df["Strategy"] > 0).mean()
    max_dd = (df["Equity"].cummax() - df["Equity"]).max()

    return {
        "Total Return %": round(total_return * 100, 2),
        "Win Rate %": round(win_rate * 100, 2),
        "Max Drawdown %": round(max_dd * 100, 2)
    }


# ============================
# PLOT EQUITY
# ============================
def plot_equity(df, title="AI V3 FAST – Equity Curve"):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Equity"], label="Strategy Equity")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    return fig


# ============================
# STREAMLIT UI
# ============================
st.title("🚀 AI V3 FAST – Neural Trading Engine")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Ticker", "MSFT")
with col2:
    period = st.selectbox("Period", ["1y", "3y", "5y", "10y"], index=2)

run = st.button("Run AI Model")

if run:
    st.write("Downloading data...")
    df = yf.download(ticker, period=period, interval="1d")

    if df.empty:
        st.error("No data downloaded. Check ticker or period.")
    else:
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

        st.write("Running AI V3 FAST...")
        df = ai_v3_fast(df)

        st.write("Auto‑Tuning thresholds...")
        df = auto_tune(df)

        st.write("Backtesting...")
        df = backtest(df)

        st.subheader("📊 Performance")
        st.write(performance(df))

        st.subheader("📈 Equity Curve")
        fig = plot_equity(df, title=f"AI V3 FAST – Equity Curve ({ticker})")
        st.pyplot(fig)

        st.subheader("📄 Last 50 rows")
        st.dataframe(df.tail(50))
