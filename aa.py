import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simple Trading Engine", layout="wide")

# ============================
# SIMPLE SIGNAL
# ============================
def simple_signal(df):
    df = df.copy()
    df["Signal"] = np.where(df["Close"] > df["Close"].shift(1), 1, -1)
    df["Signal"].fillna(0, inplace=True)
    return df

# ============================
# SIMPLE BACKTEST
# ============================
def simple_backtest(df):
    df = df.copy()

    closes = df["Close"].to_numpy()
    n = len(df)

    returns = np.zeros(n)
    for i in range(1, n):
        if closes[i-1] == 0 or np.isnan(closes[i]) or np.isnan(closes[i-1]):
            returns[i] = 0
        else:
            returns[i] = (closes[i] - closes[i-1]) / closes[i-1]

    signal = df["Signal"].to_numpy()

    strategy = np.zeros(n)
    for i in range(1, n):
        strategy[i] = signal[i-1] * returns[i]

    df["Return"] = returns
    df["Strategy"] = strategy
    df["Equity"] = np.cumprod(1 + strategy)

    return df

# ============================
# PLOT
# ============================
def plot_equity(df):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Equity"], label="Equity")
    ax.grid(True)
    ax.legend()
    return fig

# ============================
# UI
# ============================
st.title("📉 Simple Trading Engine")

col1, col2 = st.columns(2)
with col1:
    ticker = st.text_input("Ticker", "MSFT")
with col2:
    period = st.selectbox("Period", ["1y", "3y", "5y"], index=0)

run = st.button("Run")

if run:
    st.write("Downloading data...")
    df = yf.download(ticker, period=period, interval="1d")

    if df.empty:
        st.error("No data downloaded.")
    else:
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()

        st.write("Generating signals...")
        df = simple_signal(df)

        st.write("Backtesting...")
        df = simple_backtest(df)

        st.subheader("📈 Equity Curve")
        fig = plot_equity(df)
        st.pyplot(fig)

        st.subheader("📊 Last 50 rows")
        st.dataframe(df.tail(50))
