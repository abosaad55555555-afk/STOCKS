import yfinance as yf
import pandas as pd
import numpy as np
import random

START = "2010-01-01"
MAX_HOLD_DAYS = 5
PROFIT_TARGET = 0.20
STOP_LOSS = -0.10


def normalize(df):
    cols = ["Open", "High", "Low", "Close", "Volume"]
    out = {}
    for c in cols:
        out[c] = pd.to_numeric(df[c], errors="coerce") if c in df else np.nan
    return pd.DataFrame(out, index=df.index)


def compute_rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(length).mean()
    avg_loss = loss.rolling(length).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))


def detect_hammer(df):
    o = df["Open"]
    c = df["Close"]
    h = df["High"]
    l = df["Low"]

    body = (c - o).abs()
    candle_range = h - l
    lower_shadow = (o.where(o < c, c) - l)
    upper_shadow = (h - o.where(o > c, c))

    return (
        (candle_range > 0) &
        (body <= candle_range * 0.4) &
        (lower_shadow >= candle_range * 0.4) &
        (upper_shadow <= candle_range * 0.2)
    )


def load_spy_regime():
    raw = yf.download("SPY", start=START, auto_adjust=False, progress=False)
    if raw.empty:
        return pd.Series(False, index=pd.date_range(start=START, periods=5000, freq="D"))

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.columns = [c.capitalize() for c in raw.columns]

    raw["Sma200"] = raw["Close"].rolling(200).mean()
    raw["Bull"] = raw["Close"] > raw["Sma200"]
    return raw["Bull"]


def backtest_ticker(ticker, spy_bull):
    try:
        df_raw = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df_raw.empty:
            return f"{ticker}: DATA EMPTY"

        df = normalize(df_raw)

        # مؤشرات
        df["Hammer"] = detect_hammer(df)
        df["Rsi"] = compute_rsi(df["Close"])
        df["Sma10"] = df["Close"].rolling(10).mean()
        df["Sma20"] = df["Close"].rolling(20).mean()
        df["Downtrend"] = (df["Close"] < df["Sma10"]) & (df["Sma10"] < df["Sma20"])
        df["Vol20"] = df["Volume"].rolling(20).mean()
        vwap = (df["Close"] * df["Volume"]).rolling(60).sum() / df["Volume"].rolling(60).sum()
        df["Nearvwap"] = (df["Low"] <= vwap) & (df["High"] >= vwap)
        df["Confirm"] = df["Close"].shift(-1) > df["High"]
        df["Bull"] = spy_bull.reindex(df.index).fillna(False)

        # LOG لكل فلتر
        log = (
            f"{ticker}:\n"
            f"  rows: {len(df)}\n"
            f"  hammer: {df['Hammer'].sum()}\n"
            f"  downtrend: {df['Downtrend'].sum()}\n"
            f"  confirm: {df['Confirm'].sum()}\n"
            f"  rsi(20-70): {df['Rsi'].between(20,70).sum()}\n"
            f"  vol filter: {(df['Volume'] > 0.7*df['Vol20']).sum()}\n"
            f"  near vwap: {df['Nearvwap'].sum()}\n"
            f"  bull: {df['Bull'].sum()}\n"
        )

        # الإشارة الأصلية
        df["Signal"] = (
            df["Hammer"]
            & df["Downtrend"]
            & df["Confirm"]
            & df["Rsi"].between(20, 70)
            & (df["Volume"] > 0.7 * df["Vol20"])
            & df["Nearvwap"]
            & df["Bull"]
        )

        log += f"  FINAL SIGNALS: {df['Signal'].sum()}\n"

        return log

    except Exception as e:
        return f"{ticker}: ERROR {e}"
