```python
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# ----------------- إعدادات عامة -----------------
START = "2010-01-01"

# ملاحظة: يمكنك استبدال هذه القائمة بقائمة الـ 600 تيكر الكاملة التي استخدمناها سابقاً
LIQUID_TICKERS = [
    "AAPL","MSFT","AMZN","NVDA","META","GOOGL","GOOG","TSLA","AVGO","BRK.B",
    "JPM","V","MA","HD","PG","XOM","UNH","LLY","JNJ","COST","BAC",
    "WMT","MRK","PEP","KO","ABBV","CVX","ADBE","CRM","NFLX","ACN",
    "LIN","MCD","AMD","TMO","WFC","INTC","TXN","MS","PM","NEE",
    "UNP","IBM","HON","AMGN","LOW","CAT","ORCL","GS","SPGI","BLK",
    "RTX","NOW","QCOM","AMAT","BKNG","GE","MDT","ISRG","SYK","LMT",
    "DE","AXP","ADI","SCHW","CB","PLD","ELV","MMC","PFE","C",
    "MO","DUK","SO","CI","GILD","REGN","ADP","BDX","USB","TGT",
    "ZTS","CSCO","VRTX","EQIX","ICE","FDX","NSC","CL","AON","APD",
]

# ----------------- CSS مخصص لستايل Dark Premium -----------------
def load_custom_css():
    css = """
    <style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3, h4 {
        color: #FFD700 !important;
        font-weight: 700;
    }
    .stCard {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 10px;
    }
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        border-radius: 8px;
        font-weight: 700;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #C9A300;
        color: #000000;
    }
    section[data-testid="stSidebar"] {
        background-color: #0A0A0A;
        border-right: 1px solid #333333;
    }
    .dataframe {
        background-color: #1A1A1A !important;
        color: #FFFFFF !important;
    }
    a {
        color: #FFD700 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ----------------- عناصر واجهة جاهزة -----------------
def metric_card(title, value):
    st.markdown(
        f"""
        <div class='stCard'>
            <h3>{title}</h3>
            <h2 style='color:#FFD700;'>{value}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

def plot_equity_curve(equity, title):
    if equity is None or equity.empty:
        return
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=equity.index,
            y=equity.values,
            mode="lines",
            line=dict(color="#FFD700", width=3),
            name="Equity",
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="white"),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------- دوال المساعدة الأساسية -----------------
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

def compute_atr(df, length=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(length, min_periods=1).mean()
    return atr

def detect_hammer(df):
    o = df["Open"]
    c = df["Close"]
    h = df["High"]
    l = df["Low"]

    body = (c - o).abs()
    candle_range = h - l
    lower_shadow = (o.where(o < c, c) - l)
    upper_shadow = (h - o.where(o > c, c))

    cond_basic = (
        (candle_range > 0) &
        (body <= candle_range * 0.30) &
        (lower_shadow >= candle_range * 0.55) &
        (upper_shadow <= candle_range * 0.20)
    )
    cond_bullish = c >= o
    return cond_basic & cond_bullish

def load_spy_regime():
    raw = yf.download("SPY", start=START, auto_adjust=False, progress=False)

    if raw is None or raw.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(False, index=idx)

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    raw.columns = [str(c).capitalize() for c in raw.columns]
    raw = raw.apply(pd.to_numeric, errors="coerce")
    raw = raw.dropna(subset=["Close"])

    raw["Sma200"] = raw["Close"].rolling(200, min_periods=1).mean()
    raw["Bull"] = raw["Close"] > raw["Sma200"]

    raw = raw.ffill().bfill()
    return raw["Bull"]

# ----------------- Balanced V2.5 – Aggressive Enhanced Signals -----------------
def build_signals(df, spy_bull):
    df["Hammer"] = detect_hammer(df)
    df["Rsi"] = compute_rsi(df["Close"])
    df["Atr14"] = compute_atr(df, 14)
    df["Sma10"] = df["Close"].rolling(10, min_periods=1).mean()
    df["Sma20"] = df["Close"].rolling(20, min_periods=1).mean()
    df["Sma50"] = df["Close"].rolling(50, min_periods=1).mean()
    df["Vol20"] = df["Volume"].rolling(20, min_periods=1).mean()

    df["Trend"] = (df["Sma10"] < df["Sma20"]) & (df["Sma20"] < df["Sma50"])
    df["Confirm"] = df["Close"].shift(-1) > df["High"]

    candle_range = df["High"] - df["Low"]
    strong_range = candle_range > 0.30 * df["Atr14"]

    df["VolFilter"] = df["Atr14"] > df["Atr14"].rolling(50, min_periods=1).mean()
    df["NoSpike"] = (df["High"] - df["Low"]) < df["Atr14"] * 3
    df["Bull"] = spy_bull.reindex(df.index).fillna(False)

    df["Signal"] = (
        df["Hammer"]
        & df["Trend"]
        & df["Confirm"]
        & df["VolFilter"]
        & df["NoSpike"]
        & df["Rsi"].between(15, 68)
        & (df["Volume"] > 0.50 * df["Vol20"])
        & df["Bull"]
        & strong_range
    )

    return df

# ----------------- صفقات: دخول Next Open خروج Same Close -----------------
def simulate_trades(df, ticker, mode="stock"):
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

        if mode == "call_3x":
            leverage = 3.0
            ret = ((exit_close - entry_open) / entry_open) * leverage
            ret = max(ret, -1.0)
        elif mode == "call_5x":
            leverage = 5.0
            ret = ((exit_close - entry_open) / entry_open) * leverage
            ret = max(ret, -1.0)
        else:
            ret = (exit_close - entry_open) / entry_open

        trades.append(
            {
                "ticker": ticker,
                "entry_date": entry_date,
                "entry_price": entry_open,
                "exit_date": entry_date,
                "exit_price": exit_close,
                "exit_reason": "EOD",
                "return_pct": ret * 100.0,
            }
        )

    if not trades:
        return pd.DataFrame()

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

def equity_curve_from_trades(trades_df):
    if trades_df.empty:
        return pd.Series(dtype=float)
    eq = (1 + trades_df["return_pct"] / 100.0).cumprod()
    eq.index = trades_df["exit_date"]
    return eq

def backtest_ticker(ticker, spy_bull, mode="stock"):
    try:
        df_raw = yf.download(ticker, start=START, auto_adjust=False, progress=False)
        if df_raw is None or df_raw.empty:
            return {
                "log": f"{ticker}: DATA EMPTY",
                "summary": None,
                "trades": pd.DataFrame(),
                "equity": pd.Series(dtype=float),
            }

        df = normalize(df_raw)
        df = build_signals(df, spy_bull)

        log = (
            f"{ticker}:\n"
            f"  rows: {len(df)}\n"
            f"  signals: {df['Signal'].sum()}\n"
        )

        trades_df = simulate_trades(df, ticker, mode=mode)
        summary = summarize_trades(trades_df)
        equity = equity_curve_from_trades(trades_df)

        return {
            "log": log,
            "summary": summary,
            "trades": trades_df,
            "equity": equity,
        }

    except Exception as e:
        return {
            "log": f"{ticker}: ERROR {e}",
            "summary": None,
            "trades": pd.DataFrame(),
            "equity": pd.Series(dtype=float),
        }

def build_portfolio_equity(all_trades_df):
    if all_trades_df.empty:
        return pd.Series(dtype=float)
    all_trades_df = all_trades_df.sort_values("exit_date").copy()
    eq = (1 + all_trades_df["return_pct"] / 100.0).cumprod()
    eq.index = all_trades_df["exit_date"]
    return eq

# ----------------- واجهة Streamlit Pro Edition -----------------
st.set_page_config(
    page_title="HAMMER PRO – Balanced V2.5 Aggressive",
    layout="wide",
)

load_custom_css()

# Landing / Hero
st.markdown(
    """
    <div style='text-align:center; padding:40px 10px 10px 10px;'>
        <h1>HAMMER PRO</h1>
        <h3>منصة احترافية لاكتشاف شموع Hammer عالية الدقة</h3>
        <p style='color:#BFBFBF; font-size:18px;'>
            Balanced V2.5 – Aggressive Enhanced<br>
            Backtesting • Options Simulation • Portfolio Engine
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("---")

# Sidebar
st.sidebar.title("HAMMER PRO")
st.sidebar.markdown("منصة باك تست احترافية لشموع Hammer.")
mode_label = st.sidebar.selectbox(
    "نوع التنفيذ:",
    ["Stocks (بدون رافعة)", "Call Options 3x", "Call Options 5x"],
)

if mode_label == "Stocks (بدون رافعة)":
    mode = "stock"
elif mode_label == "Call Options 3x":
    mode = "call_3x"
else:
    mode = "call_5x"

selected_tickers = st.sidebar.multiselect(
    "اختر الأسهم:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:20],
)

run_button = st.sidebar.button("ابدأ الباك تست")

# Main content
with st.spinner("جاري تحميل بيانات SPY (Regime Filter)..."):
    spy_regime = load_spy_regime()
st.success("تم تحميل بيانات SPY بنجاح.")

if run_button:
    if not selected_tickers:
        st.warning("اختر سهم واحد على الأقل من القائمة في السايدبار.")
    else:
        st.write("## نتائج الباك تست")
        all_summaries = []
        all_trades_list = []

        for ticker in selected_tickers:
            st.write("---")
            st.subheader(f"🔍 {ticker}")

            with st.spinner(f"تشغيل الباك تست لـ {ticker}..."):
                result = backtest_ticker(ticker, spy_regime, mode=mode)

            st.write("#### Log")
            st.code(result["log"])

            summary = result["summary"]
            trades_df = result["trades"]
            equity = result["equity"]

            if summary:
                st.write("#### Summary (بطاقات)")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    metric_card("عدد الصفقات", summary["trades"])
                with c2:
                    metric_card("Win Rate", f"{summary['win_rate']:.1f}%")
                with c3:
                    metric_card("Avg Return", f"{summary['avg_return']:.2f}%")
                with c4:
                    metric_card("Cumulative", f"{summary['cum_return']:.2f}%")

                row = summary.copy()
                row["ticker"] = ticker
                all_summaries.append(row)

            if not trades_df.empty:
                st.write("#### الصفقات")
                st.dataframe(trades_df)
                all_trades_list.append(trades_df)
            else:
                st.info("لا توجد صفقات لهذا السهم وفق الشروط الحالية.")

            if not equity.empty:
                st.write("#### Equity Curve (سهم واحد)")
                plot_equity_curve(equity, f"Equity Curve – {ticker}")

        if all_summaries:
            st.write("---")
            st.write("## مقارنة بين الأسهم")
            summary_df = pd.DataFrame(all_summaries).set_index("ticker")
            st.dataframe(summary_df.sort_values("cum_return", ascending=False))

            st.write("#### عائد تراكمي لكل سهم")
            sorted_df = summary_df.sort_values("cum_return", ascending=False)
            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(
                    x=sorted_df.index,
                    y=sorted_df["cum_return"],
                    marker_color="#FFD700",
                )
            )
            fig_bar.update_layout(
                template="plotly_dark",
                paper_bgcolor="#000000",
                plot_bgcolor="#000000",
                font=dict(color="white"),
                xaxis_tickangle=-45,
                title="Cumulative Return per Stock",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        if all_trades_list:
            st.write("---")
            st.write("## محفظة كاملة (كل الصفقات من كل الأسهم)")
            portfolio_trades = pd.concat(all_trades_list, ignore_index=True)
            portfolio_equity = build_portfolio_equity(portfolio_trades)

            st.write("#### Equity Curve للمحفظة")
            plot_equity_curve(portfolio_equity, "Portfolio Equity Curve")

            port_summary = summarize_trades(portfolio_trades)
            st.write("#### Summary للمحفظة")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                metric_card("عدد الصفقات", port_summary["trades"])
            with c2:
                metric_card("Win Rate", f"{port_summary['win_rate']:.1f}%")
            with c3:
                metric_card("Avg Return", f"{port_summary['avg_return']:.2f}%")
            with c4:
                metric_card("Cumulative", f"{port_summary['cum_return']:.2f}%")

        st.success("تم الانتهاء من الباك تست.")
else:
    st.info("استخدم السايدبار لاختيار الأسهم ونوع التنفيذ، ثم اضغط على 'ابدأ الباك تست'.")
```