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
        (body <= candle_range * 0.4) &         # small body
        (lower_shadow >= candle_range * 0.4) & # long lower wick
        (upper_shadow <= candle_range * 0.2)   # tiny upper wick
    )


def simulate_option(stock_return):
    if stock_return >= PROFIT_TARGET:
        return min(stock_return * random.uniform(1.5, 2.0), 1.0)
    elif stock_return <= STOP_LOSS:
        return max(stock_return * random.uniform(1.5, 2.5), -0.9)
    else:
        return stock_return * random.uniform(1.0, 1.5)


def load_spy_regime():
    raw = None
    for _ in range(5):
        raw = yf.download("SPY", start=START, auto_adjust=False, progress=False)
        if isinstance(raw, pd.DataFrame) and not raw.empty:
            break

    if not isinstance(raw, pd.DataFrame) or raw.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(True, index=idx)

    spy = raw.copy()

    if isinstance(spy.columns, pd.MultiIndex):
        spy.columns = spy.columns.get_level_values(0)

    spy.columns = [str(c).capitalize() for c in spy.columns]

    required = ["Open", "High", "Low", "Close", "Volume"]
    for col in required:
        if col not in spy.columns:
            spy[col] = np.nan

    spy = spy.apply(pd.to_numeric, errors="coerce")
    spy = spy.dropna(subset=["Close"])

    if spy.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(True, index=idx)

    spy["Sma200"] = spy["Close"].rolling(200, min_periods=1).mean()
    spy = spy.ffill().bfill()

    spy["Bull"] = spy["Close"] > spy["Sma200"]
    return spy["Bull"]


def backtest_ticker(ticker, spy_bull):
    try:
        df = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df.empty:
            return None

        df = normalize(df)

        # very loose price floor
        if df["Close"].iloc[-1] < 1:
            return None

        df["Rsi"] = compute_rsi(df["Close"])
        df["Hammer"] = detect_hammer(df)

        # SIMPLE SIGNAL: hammer only (to guarantee trades)
        df["Signal"] = df["Hammer"]

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
