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


def load_spy_regime():
    # نخلّيها موجودة لو حبيت تستخدمها لاحقاً، لكنها غير مؤثرة الآن
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


def simulate_option(stock_return):
    if stock_return >= PROFIT_TARGET:
        return min(stock_return * random.uniform(1.5, 2.0), 1.0)
    elif stock_return <= STOP_LOSS:
        return max(stock_return * random.uniform(1.5, 2.5), -0.9)
    else:
        return stock_return * random.uniform(1.0, 1.5)


def backtest_ticker(ticker, spy_bull):
    try:
        df = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df.empty:
            print(f"{ticker}: EMPTY from yfinance")
            return None

        df = normalize(df)

        # لو كل الأعمدة NaN → نعتبره فاضي
        if df["Close"].isna().all():
            print(f"{ticker}: all NaN after normalize")
            return None

        # DEBUG: اطبع أول كم سطر في اللوق
        print(f"{ticker} head:\n", df.head())

        # أبسط إشارة ممكنة: كل يوم (ما عدا آخر MAX_HOLD_DAYS) هو إشارة
        df["Signal"] = False
        if len(df) > MAX_HOLD_DAYS + 1:
            df.iloc[:-MAX_HOLD_DAYS, df.columns.get_loc("Signal")] = True
        else:
            df["Signal"] = True  # لو السهم قصير التاريخ، خله كله إشارات

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

        if not trades:
            print(f"{ticker}: no trades even with trivial signal")
            return None

        return pd.DataFrame(trades)

    except Exception as e:
        print(f"ERROR {ticker}: {e}")
        return None
