import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI V3 LITE", layout="wide")


# ============================
# AI ENGINE (SAFE)
# ============================
def ai_engine(df):
    df = df.copy()

    # simple features
    body = (df["Close"] - df["Open"]).abs().to_numpy()
    range_ = (df["High"] - df["Low"]).to_numpy()
    dir_ = np.sign(df["Close"] - df["Open"]).to_numpy()

    # avoid division by zero
    range_[range_ == 0] = 1e-9

    body_pct = body / range_

    # prediction = weighted body * direction
    pred = body_pct * dir_

    # boost
    pred = pred * 3

    df["AI_Pred"] = pred
    return df


# ============================
# BACKTEST (SUPER SAFE)
# ============================
def backtest(df):
    df = df.copy()

    closes = df["Close"].to_numpy()
    pred = df["AI_Pred"].to_numpy()

    n = len(df)

    # --- Trend (simple MA 10) ---
    trend = np.zeros(n)
    for i in range(n):
        start = max(0, i - 9)
        trend[i] = closes[start:i+1].mean()

    # --- TrendSignal ---
    trend_signal = np.where(closes > trend, 1, -1)

    # --- Signals ---
    signal = np.where(pred > 0, 1, -1)
    signal = signal * trend_signal

    # --- SAFE RETURNS ---
    returns = np.zeros(n)
    for i in range(1, n):
        if closes[i-1] == 0 or np.isnan(closes[i]) or np.isnan(closes[i-1]):
            returns[i] = 0
        else:
            returns[i] = (closes[i] - closes[i-1]) / closes[i-1]

    # --- Strategy ---
    strategy = np.zeros(n)
    for i in range(1, n):
        strategy[i] = signal[i-1] * returns[i]

    equity = np.cumprod(1 + strategy)

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
def plot_equity(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Equity"], label="Equity")
    ax.grid(True)
    ax.legend()
    return fig


# ============================
# STREAMLIT UI
# ============================
st.title("🚀 AI V3 LITE – Stable Trading Engine")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Ticker", "MSFT")
with col2:
    period = st.selectbox("Period", ["1y", "3y", "5y"], index=0)

run = st.button("Run AI Model")

if run:
    st.write("Downloading data...")
    df = yf.download(ticker, period=period, interval="1d")

    if df.empty:
        st.error("No data downloaded.")
    else:
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

        st.write("Running AI Engine...")
        df = ai_engine(df)

        st.write("Backtesting...")
        df = backtest(df)

        st.subheader("📊 Performance")
        st.write(performance(df))

        st.subheader("📈 Equity Curve")
        fig = plot_equity(df)
        st.pyplot(fig)

        st.subheader("📄 Last 50 rows")
        st.dataframe(df.tail(50))
