import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

START = "2010-01-01"


def load_custom_css():
    css = """
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; font-family: 'Poppins', sans-serif; }
    h1, h2, h3, h4 { color: #FFD700 !important; font-weight: 700; }
    .stCard { background-color: #1A1A1A !important; border: 1px solid #333333 !important;
              border-radius: 12px; padding: 20px; margin-bottom: 10px; }
    .stButton>button { background-color: #FFD700; color: #000000; border-radius: 8px;
                       font-weight: 700; border: none; padding: 10px 20px; }
    .stButton>button:hover { background-color: #C9A300; color: #000000; }
    section[data-testid="stSidebar"] { background-color: #0A0A0A; border-right: 1px solid #333333; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def metric_card(title, value):
    st.markdown(
        f"<div class='stCard'><h3>{title}</h3><h2 style='color:#FFD700;'>{value}</h2></div>",
        unsafe_allow_html=True,
    )


def plot_equity_curve(equity, title):
    if equity is None or equity.empty:
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=equity.index, y=equity.values,
                             mode='lines', line=dict(color='#FFD700', width=3)))
    fig.update_layout(template='plotly_dark', paper_bgcolor='#000000',
                      plot_bgcolor='#000000', font=dict(color='white'),
                      height=350, title=title)
    st.plotly_chart(fig, use_container_width=True)


def normalize(df):
    cols = ["Open", "High", "Low", "Close", "Volume"]
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).capitalize() for c in df.columns]
    out = {
        c: pd.to_numeric(df[c], errors="coerce") if c in df else pd.Series(np.nan, index=df.index)
        for c in cols
    }
    return pd.DataFrame(out, index=df.index)


def compute_rsi(series, length=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(length, min_periods=1).mean()
    avg_loss = loss.rolling(length, min_periods=1).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    return 100 - (100 / (1 + rs))


def compute_atr(df, length=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(length, min_periods=1).mean()


def detect_hammer(df):
    o, c, h, l = df["Open"], df["Close"], df["High"], df["Low"]
    body = (c - o).abs()
    candle_range = h - l
    lower_shadow = o.where(o < c, c) - l
    upper_shadow = h - o.where(o > c, c)
    cond = (
        (candle_range > 0)
        & (body <= candle_range * 0.30)
        & (lower_shadow >= candle_range * 0.55)
        & (upper_shadow <= candle_range * 0.20)
    )
    return cond


def detect_inverted_hammer(df):
    o, c, h, l = df["Open"], df["Close"], df["High"], df["Low"]
    body = (c - o).abs()
    candle_range = h - l
    upper_shadow = h - o.where(o > c, c)
    lower_shadow = o.where(o < c, c) - l
    cond = (
        (candle_range > 0)
        & (body <= candle_range * 0.30)
        & (upper_shadow >= body * 2.0)
        & (lower_shadow <= body * 0.5)
    )
    return cond


def detect_pinbar(df):
    o, c, h, l = df["Open"], df["Close"], df["High"], df["Low"]
    body = (c - o).abs()
    candle_range = h - l
    lower_shadow = o.where(o < c, c) - l
    upper_shadow = h - o.where(o > c, c)
    cond = (
        (candle_range > 0)
        & (body <= candle_range * 0.30)
        & (lower_shadow >= body * 2.5)
        & (upper_shadow <= body * 1.0)
    )
    return cond


def load_spy_regime():
    raw = yf.download("SPY", start=START, auto_adjust=False, progress=False)
    if raw is None or raw.empty:
        idx = pd.date_range(start=START, periods=5000, freq="D")
        return pd.Series(False, index=idx)

    raw.columns = raw.columns.get_level_values(0)
    raw.columns = [str(c).capitalize() for c in raw.columns]
    raw = raw.apply(pd.to_numeric, errors="coerce").dropna(subset=["Close"])

    raw["Sma200"] = raw["Close"].rolling(200, min_periods=1).mean()
    raw["Bull"] = raw["Close"] > raw["Sma200"]

    return raw["Bull"].ffill().bfill()


def build_signals(df, spy_bull):
    df["Hammer"] = detect_hammer(df)
    df["InvHammer"] = detect_inverted_hammer(df)
    df["PinBar"] = detect_pinbar(df)
    df["Pattern"] = df["Hammer"] | df["InvHammer"] | df["PinBar"]

    df["Rsi"] = compute_rsi(df["Close"])
    df["Atr14"] = compute_atr(df)

    df["Sma5"] = df["Close"].rolling(5).mean()
    df["Sma10"] = df["Close"].rolling(10).mean()
    df["Sma20"] = df["Close"].rolling(20).mean()
    df["Sma50"] = df["Close"].rolling(50).mean()

    df["Vol20"] = df["Volume"].rolling(20).mean()
    df["Vol5"] = df["Volume"].rolling(5).mean()

    df["Trend"] = (
        (df["Sma5"] < df["Sma10"])
        & (df["Sma10"] < df["Sma20"])
        & (df["Sma20"] < df["Sma50"])
    )

    df["VolSpike"] = df["Volume"] > df["Vol20"] * 1.2
    df["VolConfirm"] = df["Vol5"] > df["Vol20"] * 0.7
    df["VolStable"] = df["Vol20"] > df["Vol20"].rolling(50).mean() * 0.6
    df["VolumeFilter"] = df["VolSpike"] & df["VolConfirm"] & df["VolStable"]

    df["ATR_Adaptive"] = df["Atr14"] > df["Atr14"].rolling(50).mean() * 0.8

    df["NoSpike"] = (df["High"] - df["Low"]) < df["Atr14"] * 2.5
    df["NoGap"] = (df["Open"] - df["Close"].shift(1)).abs() < df["Atr14"] * 1.8

    df["Bull"] = spy_bull.reindex(df.index).fillna(False)

    candle_range = df["High"] - df["Low"]
    df["StrongRange"] = candle_range > df["Atr14"] * 0.35

    df["Confirm"] = df["Close"].shift(-1) > df["High"] * 1.002

    df["Signal"] = (
        df["Pattern"]
        & df["Trend"]
        & df["VolumeFilter"]
        & df["ATR_Adaptive"]
        & df["NoSpike"]
        & df["NoGap"]
        & df["StrongRange"]
        & df["Confirm"]
        & df["Rsi"].between(10, 70)
        & df["Bull"]
    )

    return df


def simulate_trades(df, ticker, mode="stock"):
    trades = []
    for sig_date in df.index[df["Signal"]]:
        pos = df.index.get_loc(sig_date)
        if pos + 1 >= len(df):
            continue

        entry_date = df.index[pos + 1]
        entry_open = df.loc[entry_date, "Open"]
        exit_close = df.loc[entry_date, "Close"]

        if mode == "call_3x":
            ret = ((exit_close - entry_open) / entry_open) * 3
            ret = max(ret, -1)
        elif mode == "call_5x":
            ret = ((exit_close - entry_open) / entry_open) * 5
            ret = max(ret, -1)
        else:
            ret = (exit_close - entry_open) / entry_open

        trades.append(
            {
                "ticker": ticker,
                "entry_date": entry_date,
                "entry_price": entry_open,
                "exit_date": entry_date,
                "exit_price": exit_close,
                "return_pct": ret * 100,
            }
        )

    return pd.DataFrame(trades)


def summarize_trades(df):
    if df.empty:
        return {
            "trades": 0,
            "win_rate": 0,
            "avg_return": 0,
            "max_gain": 0,
            "max_loss": 0,
            "cum_return": 0,
        }

    n = len(df)
    wins = (df["return_pct"] > 0).sum()
    cum = (1 + df["return_pct"] / 100).prod() - 1

    return {
        "trades": n,
        "win_rate": wins / n * 100,
        "avg_return": df["return_pct"].mean(),
        "max_gain": df["return_pct"].max(),
        "max_loss": df["return_pct"].min(),
        "cum_return": cum * 100,
    }


def equity_curve(df):
    if df.empty:
        return pd.Series(dtype=float)
    eq = (1 + df["return_pct"] / 100).cumprod()
    eq.index = df["exit_date"]
    return eq


# =========================
#       MAIN APP
# =========================

st.set_page_config(page_title="HAMMER PRO", layout="wide")
load_custom_css()

st.markdown("<h1 style='text-align:center;'>HAMMER PRO</h1>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='text-align:center;'>Aggressive V3 – Hammer + Inverted Hammer + Pin Bar</h3>",
    unsafe_allow_html=True,
)
st.write("---")

tab_backtest, tab_scanner = st.tabs(["Backtest", "Today Scanner"])

# Execution Mode
mode_label = st.sidebar.selectbox("Execution Mode", ["Stocks", "Call 3x", "Call 5x"])
mode = "stock" if mode_label == "Stocks" else ("call_3x" if mode_label == "Call 3x" else "call_5x")

# =========================
#   TICKER UNIVERSE
# =========================

st.sidebar.markdown("### S&P 500")
sp500_list = [
    "AAPL","MSFT","AMZN","NVDA","META","GOOGL","GOOG","TSLA","BRK.B","UNH","XOM","JNJ","JPM","V","PG",
    "MA","HD","CVX","ABBV","COST","MRK","PEP","KO","WMT","AVGO","LLY","BAC","MCD","DIS","ADBE",
    "CRM","NFLX","ACN","LIN","AMD","TMO","WFC","INTC","TXN","MS","PM","NEE","UNP","IBM","HON",
    "AMGN","LOW","CAT","ORCL","GS","SPGI","BLK","NOW","GE","SBUX","BKNG","MDLZ","ISRG","ADP",
    "GILD","LMT","SYK","C","CB","CI","DE","MMC","PLD","SCHW","ZTS","AMT","MO","PGR","UPS","RTX",
    "ELV","BMY","USB","SO","TGT","ADI","REGN","EQIX","AON","BSX","CHTR","DUK","HCA","EOG","SLB",
    "TJX","PNC","CL","FDX","ICE","APD","SHW","ITW","GM","MU","CME","DHR","MCO","AEP","COP","KDP",
    "MAR","AIG","PSA","CTAS","MCK","ORLY","KLAC","NXPI","PH","TFC","SRE","MPC","OXY","MSCI",
    "CDNS","AZO","WMB","ED","D","CNC","ADM","MET","PRU","ALL","EXC","WBA","DVN","A","ROP","IDXX",
    "ECL","YUM","PAYX","TRV","WEC","VLO","CARR","KHC","GIS","KR","HES","HPQ","WBD","HAL","DAL",
    "EA","ROST","VICI","FTNT","ANET","DXCM","F","NEM","NOC","BIIB","AVB","VRSK","O","ZBH","TROW",
    "LHX","KEY","RF","HBAN","CFG","COF"
]
sp500_selected = st.sidebar.multiselect("Select from S&P 500", sp500_list)

st.sidebar.markdown("### NASDAQ 100")
nasdaq_list = [
    "AAPL","MSFT","AMZN","NVDA","META","GOOGL","GOOG","TSLA","PEP","COST","AVGO","ADBE","NFLX",
    "AMD","INTC","CSCO","CMCSA","TXN","AMGN","QCOM","HON","SBUX","AMAT","INTU","ISRG","MDLZ",
    "ADP","PYPL","MU","LRCX","BKNG","GILD","PANW","MAR","ADI","REGN","KDP","FTNT","KLAC","SNPS",
    "CDNS","MCHP","NXPI","IDXX","CPRT","VRTX","ORLY","PCAR","MNST","CHTR","AEP","KHC","WBD","EA",
    "ROST","EXC","FAST","CTAS","PAYX","XEL","VRSK","CRWD","DDOG","ZS","OKTA","MDB","ETSY","DOCU",
    "ZM","ENPH","FSLR","ABNB","SHOP","COIN","PLTR","UBER","RBLX","NET","SNOW","SMCI"
]
nasdaq_selected = st.sidebar.multiselect("Select from NASDAQ 100", nasdaq_list)

st.sidebar.markdown("### Dow Jones 30")
dow_list = [
    "AAPL","MSFT","AMGN","AXP","BA","CAT","CRM","CSCO","CVX","DIS","DOW","GS","HD","HON","IBM",
    "INTC","JNJ","JPM","KO","MCD","MMM","MRK","NKE","PG","TRV","UNH","V","VZ","WMT"
]
dow_selected = st.sidebar.multiselect("Select from Dow Jones 30", dow_list)

st.sidebar.markdown("### High Volatility")
hv_list = [
    "TSLA","NVDA","AMD","SMCI","COIN","PLTR","AFRM","RBLX","SHOP","ROKU","NET","CRWD","DDOG",
    "UPST","SQ","HOOD","ABNB","SNOW","MDB","ZS","OKTA","SMCI"
]
hv_selected = st.sidebar.multiselect("High Volatility Stocks", hv_list)

st.sidebar.markdown("### Sector ETFs")
sector_etfs = [
    "XLK","XLF","XLE","XLY","XLP","XLI","XLB","XLV","XLU","IYR","IYT","IYW","IYF","IYE"
]
sector_selected = st.sidebar.multiselect("Sector ETFs", sector_etfs)

st.sidebar.markdown("### Index ETFs")
index_etfs = [
    "SPY","QQQ","IWM","DIA","VTI","VOO","VT","SCHD","ARKK"
]
index_selected = st.sidebar.multiselect("Index ETFs", index_etfs)

tickers = list(
    set(
        sp500_selected
        + nasdaq_selected
        + dow_selected
        + hv_selected
        + sector_selected
        + index_selected
    )
)

run = st.sidebar.button("Run Backtest")
spy = load_spy_regime()

# =========================
#       BACKTEST TAB
# =========================

with tab_backtest:
    if run:
        if not tickers:
            st.warning("اختر على الأقل سهم واحد من الشريط الجانبي.")
        else:
            all_trades = []
            all_summaries = []

            for t in tickers:
                st.subheader(t)

                df_raw = yf.download(t, start=START, auto_adjust=False, progress=False)
                if df_raw.empty:
                    st.warning(f"No data for {t}")
                    continue

                df = normalize(df_raw)
                df = build_signals(df, spy)

                trades = simulate_trades(df, t, mode)
                summary = summarize_trades(trades)
                eq = equity_curve(trades)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    metric_card("Trades", summary["trades"])
                with c2:
                    metric_card("Win Rate", f"{summary['win_rate']:.1f}%")
                with c3:
                    metric_card("Avg Return", f"{summary['avg_return']:.2f}%")
                with c4:
                    metric_card("Cumulative", f"{summary['cum_return']:.2f}%")

                st.dataframe(trades)
                plot_equity_curve(eq, f"Equity Curve – {t}")

                trades["ticker"] = t
                all_trades.append(trades)
                summary["ticker"] = t
                all_summaries.append(summary)

            if all_trades:
                st.write("---")
                st.subheader("Portfolio Summary")

                port = pd.concat(all_trades)
                port_sum = summarize_trades(port)
                port_eq = equity_curve(port)

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    metric_card("Trades", port_sum["trades"])
                with c2:
                    metric_card("Win Rate", f"{port_sum['win_rate']:.1f}%")
                with c3:
                    metric_card("Avg Return", f"{port_sum['avg_return']:.2f}%")
                with c4:
                    metric_card("Cumulative", f"{port_sum['cum_return']:.2f}%")

                plot_equity_curve(port_eq, "Portfolio Equity Curve")
    else:
        st.info("اختر الأسهم واضغط Run Backtest من الشريط الجانبي.")

# =========================
#       SCANNER TAB
# =========================

with tab_scanner:
    st.subheader("Today Scanner – Live Signals")

    scan_btn = st.button("Scan Today")

    if scan_btn:
        if not tickers:
            st.warning("اختر على الأقل سهم واحد من الشريط الجانبي.")
        else:
            results = []
            spy_local = load_spy_regime()

            for t in tickers:
                df_raw = yf.download(t, period="6mo", auto_adjust=False, progress=False)
                if df_raw.empty:
                    continue

                df = normalize(df_raw)
                df = build_signals(df, spy_local)

                last_row = df.iloc[-1]
                if bool(last_row.get("Signal", False)):
                    results.append(
                        {
                            "Ticker": t,
                            "Date": df.index[-1],
                            "Close": float(last_row["Close"]),
                            "RSI": float(last_row["Rsi"]),
                            "ATR14": float(last_row["Atr14"]),
                            "Pattern": "Yes" if last_row["Pattern"] else "No",
                            "TrendOK": "Yes" if last_row["Trend"] else "No",
                            "VolumeOK": "Yes" if last_row["VolumeFilter"] else "No",
                            "SPY Bull": "Yes" if last_row["Bull"] else "No",
                        }
                    )

            if results:
                st.success(f"Found {len(results)} signals today.")
                st.dataframe(pd.DataFrame(results))
            else:
                st.info("لا توجد إشارات اليوم على الأسهم المختارة.")
