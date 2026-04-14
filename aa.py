import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="AI V3 PRO", layout="wide")


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

        moves = (
            df["Close"].values[i - lookback + 1:i + 1]
            - df["Open"].values[i - lookback + 1:i + 1]
        )

        w_sum = np.sum(sim)
        pred[i] = np.sum(sim * moves) / (w_sum + 1e-9)

    df["AI_PredMove"] = pred
    return df


def auto_tune(df, window=50):
    df = df.copy()
    df["PredAbs"] = df["AI_PredMove"].abs()
    vol = df["PredAbs"].rolling(window).std()
    df["Thr"] = vol.fillna(vol.mean() if not np.isnan(vol.mean()) else 0.0001)
    df["Thr"] = df["Thr"].replace(0, 0.0001)
    return df


def backtest(df):
    df = df.copy()

    df["Signal"] = 0
    df.loc[df["AI_PredMove"] > df["Thr"], "Signal"] = 1
    df.loc[df["AI_PredMove"] < -df["Thr"], "Signal"] = -1

    if (df["Signal"].abs().sum() == 0) and df["AI_PredMove"].abs().sum() != 0:
        df["Signal"] = 0
        df.loc[df["AI_PredMove"] > 0, "Signal"] = 1
        df.loc[df["AI_PredMove"] < 0, "Signal"] = -1

    df["Return"] = df["Close"].pct_change()
    df["Strategy"] = df["Signal"].shift(1) * df["Return"]
    df["Equity"] = (1 + df["Strategy"]).cumprod().fillna(1.0)

    return df


def performance(df):
    if "Equity" not in df or df["Equity"].dropna().empty:
        return {
            "Total Return %": 0,
            "Win Rate %": 0,
            "Max Drawdown %": 0,
            "Note": "No equity data / no trades generated."
        }

    total_return = df["Equity"].iloc[-1] - 1
    win_rate = (df["Strategy"] > 0).mean() if "Strategy" in df else 0
    max_dd = (df["Equity"].cummax() - df["Equity"]).max()

    return {
        "Total Return %": round(total_return * 100, 2),
        "Win Rate %": round(win_rate * 100, 2),
        "Max Drawdown %": round(max_dd * 100, 2)
    }


def plot_equity(df, title="AI V3 FAST – Equity Curve"):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index, df["Equity"], label="Strategy Equity")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()
    return fig


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

        if "Equity" in df and not df["Equity"].dropna().empty:
            st.subheader("📈 Equity Curve")
            fig = plot_equity(df, title=f"AI V3 FAST – Equity Curve ({ticker})")
            st.pyplot(fig)
        else:
            st.warning("No equity curve available (no trades).")

        st.subheader("📄 Last 50 rows")
        st.dataframe(df.tail(50))
