import yfinance as yf
import pandas as pd
import numpy as np
import random

START = "2010-01-01"
MAX_HOLD_DAYS = 5
PROFIT_TARGET = 0.20
STOP_LOSS = -0.10


def normalize(df):
    return df[["Open", "High", "Low", "Close", "Volume"]].copy()


def compute_rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(length).mean()
    avg_loss = loss.rolling(length).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))


def compute_atr(df, length=14):
    hl = df["High"] - df["Low"]
    hc = (df["High"] - df["Close"].shift()).abs()
    lc = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(length).mean()


def detect_hammer(df):
    o, h, l, c = df["Open"], df["High"], df["Low"], df["Close"]
    body = (c - o).abs()
    lower = (o.where(o < c, c) - l)
    upper = (h - o.where(o > c, c))
    return (body > 0) & (lower >= 2 * body) & (upper <= 0.3 * body)


def simulate_option(stock_return):
    if stock_return >= PROFIT_TARGET:
        return min(stock_return * random.uniform(1.5, 2.0), 1.0)
    elif stock_return <= STOP_LOSS:
        return max(stock_return * random.uniform(1.5, 2.5), -0.9)
    else:
        return stock_return * random.uniform(1.0, 1.5)


def load_spy_regime():
    # robust, Streamlit-safe SPY regime loader
    spy = pd.DataFrame()
    for _ in range(5):
        spy = yf.download("SPY", start=START, auto_adjust=False, progress=False)
        if not spy.empty:
            break

    if spy.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(True, index=idx)

    spy = spy[["Open", "High", "Low", "Close", "Volume"]].copy()
    spy = spy.apply(pd.to_numeric, errors="coerce")
    spy = spy.dropna(subset=["Close"])

    spy["SMA200"] = spy["Close"].rolling(200, min_periods=1).mean()
    spy = spy.fillna(method="ffill").fillna(method="bfill")

    spy["Bull"] = spy["Close"] > spy["SMA200"]
    return spy["Bull"]


def backtest_ticker(ticker, spy_bull):
    try:
        df = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df.empty:
            return None

        df = normalize(df)

        if df["Close"].iloc[-1] < 10:
            return None

        df["RSI"] = compute_rsi(df["Close"])
        df["ATR"] = compute_atr(df)
        df["Vol20"] = df["Volume"].rolling(20).mean()
        df["Hammer"] = detect_hammer(df)

        df["SMA10"] = df["Close"].rolling(10).mean()
        df["SMA20"] = df["Close"].rolling(20).mean()
        df["Downtrend"] = (df["Close"] < df["SMA10"]) & (df["SMA10"] < df["SMA20"])

        vwap = (df["Close"] * df["Volume"]).rolling(60).sum() / df["Volume"].rolling(60).sum()
        df["VWAP60"] = vwap
        df["NearVWAP"] = (df["Low"] <= vwap) & (df["High"] >= vwap)

        df["Confirm"] = df["Close"].shift(-1) > df["High"]

        df["Bull"] = spy_bull.reindex(df.index).fillna(False)

        df["Signal"] = (
            df["Hammer"]
            & df["Downtrend"]
            & df["Confirm"]
            & df["RSI"].between(20, 70)
            & (df["Volume"] > 0.7 * df["Vol20"])
            & df["NearVWAP"]
            & df["Bull"]
        )

        trades = []
        sig_idx = np.where(df["Signal"])[0]

        for i in sig_idx:
            entry_idx = i + 1
            if entry_idx >= len(df):
                continue

            entry_price = df["Open"].iloc[entry_idx]
            entry_date = df.index[entry_idx]

            exit_idx = min(entry_idx + MAX_HOLD_DAYS, len(df) - 1)
            window = df.iloc[entry_idx:exit_idx + 1]

            prices = window["Close"]
            stock_returns = (prices / entry_price) - 1

            hit_target = stock_returns >= PROFIT_TARGET
            hit_stop = stock_returns <= STOP_LOSS

            if hit_target.any():
                exit_loc = hit_target.idxmax()
            elif hit_stop.any():
                exit_loc = hit_stop.idxmax()
            else:
                exit_loc = prices.index[-1]

            exit_price = df.loc[exit_loc, "Close"]
            stock_ret = (exit_price / entry_price) - 1
            opt_ret = simulate_option(stock_ret)

            trades.append({
                "Ticker": ticker,
                "EntryDate": entry_date,
                "ExitDate": exit_loc,
                "StockReturn": stock_ret,
                "OptionReturn": opt_ret
            })

        return pd.DataFrame(trades) if trades else None

    except Exception:
        return None
