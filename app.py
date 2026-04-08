import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ----------------- إعدادات عامة -----------------
START = "2010-01-01"

LIQUID_TICKERS = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG",
    "META", "NVDA", "TSLA", "AVGO", "ADBE",
]


# ----------------- دوال المساعدة -----------------
def normalize(df):
    cols = ["Open", "High", "Low", "Close", "Volume"]
    out = {}

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.columns = [str(c).capitalize() for c in df.columns]

    for c in cols:
        if c in df:
            out[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            out[c] = pd.Series(np.nan, index=df.index)

    return pd.DataFrame(out, index=df.index)


def compute_rsi(series, length=14):
    series = pd.to_numeric(series, errors="coerce")
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(length, min_periods=1).mean()
    avg_loss = loss.rolling(length, min_periods=1).mean()
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

    if raw is None or raw.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(False, index=idx)

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.columns = [str(c).capitalize() for c in raw.columns]

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col not in raw.columns:
            raw[col] = np.nan

    raw = raw.apply(pd.to_numeric, errors="coerce")
    raw = raw.dropna(subset=["Close"])

    raw["Sma200"] = raw["Close"].rolling(200, min_periods=1).mean()
    raw["Bull"] = raw["Close"] > raw["Sma200"]

    raw = raw.ffill().bfill()

    return raw["Bull"]


# ----------------- بناء الإشارات -----------------
def build_signals(df, spy_bull):
    df["Hammer"] = detect_hammer(df)
    df["Rsi"] = compute_rsi(df["Close"])
    df["Sma10"] = df["Close"].rolling(10, min_periods=1).mean()
    df["Sma20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["Downtrend"] = (df["Close"] < df["Sma10"]) & (df["Sma10"] < df["Sma20"])
    df["Vol20"] = df["Volume"].rolling(20, min_periods=1).mean()

    df["Confirm"] = df["Close"].shift(-1) > df["High"]
    df["Bull"] = spy_bull.reindex(df.index).fillna(False)

    df["Signal"] = (
        df["Hammer"]
        & df["Downtrend"]
        & df["Confirm"]
        & df["Rsi"].between(20, 70)
        & (df["Volume"] > 0.7 * df["Vol20"])
        & df["Bull"]
    )

    return df


# ----------------- صفقات: دخول Next Open خروج Same Close -----------------
def simulate_trades(df):
    trades = []
    signal_dates = df.index[df["Signal"]].tolist()

    for sig_date in signal_dates:
        pos = df.index.get_loc(sig_date)
        if pos + 1 >= len(df):
            continue

        entry_date = df.index[pos + 1]
        entry_open = df.loc[entry_date, "Open"]
        exit_close = df.loc[entry_date, "Close"]

        if pd.isna(entry_open) or pd.isna(exit_close):
            continue

        ret = (exit_close - entry_open) / entry_open

        trades.append(
            {
                "entry_date": entry_date,
                "entry_price": entry_open,
                "exit_date": entry_date,
                "exit_price": exit_close,
                "exit_reason": "EOD",
                "return_pct": ret * 100.0,
            }
        )

    if not trades:
        return pd.DataFrame(columns=["entry_date", "entry_price", "exit_date", "exit_price", "exit_reason", "return_pct"])

    trades_df = pd.DataFrame(trades)
    trades_df.sort_values("entry_date", inplace=True)
    trades_df.reset_index(drop=True, inplace=True)
    return trades_df


def summarize_trades(trades_df):
    if trades_df.empty:
        return {
            "trades": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "max_gain": 0.0,
            "max_loss": 0.0,
            "cum_return": 0.0,
        }

    n = len(trades_df)
    wins = (trades_df["return_pct"] > 0).sum()
    win_rate = wins / n * 100.0
    avg_return = trades_df["return_pct"].mean()
    max_gain = trades_df["return_pct"].max()
    max_loss = trades_df["return_pct"].min()
    cum_return = (1 + trades_df["return_pct"] / 100.0).prod() - 1

    return {
        "trades": n,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "max_gain": max_gain,
        "max_loss": max_loss,
        "cum_return": cum_return * 100.0,
    }


# ----------------- الباك تست الرئيسي -----------------
def backtest_ticker(ticker, spy_bull):
    try:
        df_raw = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df_raw is None or df_raw.empty:
            return {"log": f"{ticker}: DATA EMPTY", "summary": None, "trades": pd.DataFrame()}

        df = normalize(df_raw)

        if df["Close"].isna().all():
            return {"log": f"{ticker}: ERROR – Close prices all NaN", "summary": None, "trades": pd.DataFrame()}

        df = build_signals(df, spy_bull)

        log = (
            f"{ticker}:\n"
            f"  rows: {len(df)}\n"
            f"  signals: {df['Signal'].sum()}\n"
        )

        trades_df = simulate_trades(df)
        summary = summarize_trades(trades_df)

        return {"log": log, "summary": summary, "trades": trades_df}

    except Exception as e:
        return {"log": f"{ticker}: ERROR {e}", "summary": None, "trades": pd.DataFrame()}


# ----------------- واجهة Streamlit -----------------
st.set_page_config(page_title="Hammer Backtest – Intraday", layout="wide")

st.title("Hammer Backtest – دخول Next Open وخروج Same Close")
st.write("هذا النموذج يحول إشارات الهامر إلى صفقات يومية بدون VWAP.")

with st.spinner("جاري تحميل بيانات SPY..."):
    spy_regime = load_spy_regime()
st.success("تم تحميل بيانات SPY بنجاح.")

selected_tickers = st.multiselect(
    "اختر الأسهم:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:10],
)

run_button = st.button("ابدأ الباك تست")

if run_button:
    if not selected_tickers:
        st.warning("اختر سهم واحد على الأقل.")
    else:
        st.write("### النتائج")

        for ticker in selected_tickers:
            st.write("---")
            st.subheader(f"🔍 {ticker}")

            with st.spinner(f"تشغيل الباك تست لـ {ticker}..."):
                result = backtest_ticker(ticker, spy_regime)

            st.write("#### Log")
            st.code(result["log"])

            summary = result["summary"]
            trades_df = result["trades"]

            if summary:
                st.write("#### Summary")
                st.write(
                    f"- عدد الصفقات: {summary['trades']}\n"
                    f"- نسبة الربح: {summary['win_rate']:.1f}%\n"
                    f"- متوسط العائد: {summary['avg_return']:.2f}%\n"
                    f"- أكبر ربح: {summary['max_gain']:.2f}%\n"
                    f"- أكبر خسارة: {summary['max_loss']:.2f}%\n"
                    f"- العائد التراكمي: {summary['cum_return']:.2f}%"
                )

            if not trades_df.empty:
                st.write("#### الصفقات")
                st.dataframe(trades_df)
            else:
                st.info("لا توجد صفقات.")

        st.success("تم الانتهاء.")
