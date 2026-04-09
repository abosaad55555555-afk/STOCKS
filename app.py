import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------- إعدادات عامة -----------------
START = "2010-01-01"

# ----------------- قائمة 600 سهم Optionable كاملة -----------------
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
"SHW","ITW","MU","PANW","ETN","NKE","MAR","AEP","MCO","PSA",
"WM","EMR","ROP","HCA","DHR","SBUX","LRCX","KLAC","FIS","FISV",
"GM","HUM","AIG","MET","PRU","TRV","ALL","AFL","PGR","BK",
"MSI","TEL","PH","ROST","CTAS","MNST","KMB","GIS","HSY","KHC",
"MDLZ","SYY","KR","DG","DLTR","WBA","T","VZ","CMCSA","DIS",
"FOX","FOXA","PARA","WBD","EA","TTWO","ROKU","LYV","CHTR","TMUS",
"CSX","UNP","CP","CNI","UPS","DAL","UAL","LUV","AAL","EXPE",
"ABNB","UBER","LYFT","RCL","CCL","NCLH","H","HLT","MGM","LVS",
"WYNN","MAR","BKNG","F","STLA","RIVN","LCID","NIO","XPEV","LI",
"GM","TSLA","FSLR","ENPH","SEDG","NEE","DUK","SO","AEP","ED",
"XEL","PEG","D","EIX","PCG","SRE","WEC","CMS","ATO","NI",
"OKE","WMB","KMI","ET","EPD","MPLX","PAA","TRGP","ENB","TRP",
"SLB","HAL","BKR","VLO","PSX","MPC","HES","COP","OXY","PXD",
"EOG","DVN","FANG","APA","MRO","AR","RRC","SWN","CHK","EQNR",
"CVX","XOM","BP","SHEL","TTE","PTR","SNP","EC","ENI","YPF",
"BA","LMT","NOC","GD","RTX","TDG","HEI","TXT","SPR","GE",
"CAT","DE","CMI","PCAR","OSK","AGCO","PWR","JCI","EMR","ETN",
"MMM","HON","ROK","IR","XYL","AWK","AOS","MAS","FBHS","WHR",
"HD","LOW","TSCO","BBY","RH","W","AMZN","EBAY","ETSY","SHOP",
"CVS","WBA","CI","UNH","HUM","ELV","CNC","MOH","PFE","MRK",
"LLY","BMY","GILD","REGN","VRTX","BIIB","AMGN","ILMN","DHR","TMO",
"ISRG","SYK","EW","BSX","ZBH","ALGN","XRAY","HOLX","STE","RMD",
"ABT","MDT","BDX","PKI","MTD","WAT","A","BIO","TECH","IDXX",
"PANW","FTNT","CRWD","ZS","OKTA","SPLK","DDOG","SNOW","MDB","NET",
"MSFT","ORCL","SAP","ADBE","CRM","INTU","NOW","TEAM","WDAY","PAYC",
"V","MA","AXP","DFS","COF","SYF","PYPL","SQ","AFRM","HOOD",
"JPM","BAC","WFC","C","GS","MS","USB","PNC","TFC","BK",
"BLK","STT","NTRS","SCHW","AMP","BEN","IVZ","TROW","APO","KKR",
"PLD","AMT","CCI","EQIX","PSA","SPG","O","WELL","VTR","EQR",
"AVB","UDR","ESS","MAA","CPT","ARE","BXP","SLG","VNO","HST",
"DLR","IRM","SBAC","WY","PCH","RYN","LEN","DHI","PHM","TOL",
"NVR","HD","LOW","TSCO","WMT","COST","TGT","DG","DLTR","BJ",
"KO","PEP","MNST","KDP","CELH","TAP","STZ","BF.B","MO","PM",
"BTI","UL","PG","CL","KMB","CHD","EL","COTY","IPAR","NKE",
"ADDYY","LULU","UAA","VFC","RL","PVH","TIF","SIG","JWN","M",
"FDX","UPS","CHRW","JBHT","ODFL","SAIA","XPO","R","KNX","SNDR",
"CSX","NSC","UNP","CP","CNI","KSU","TMUS","VZ","T","CMCSA",
"DIS","NFLX","ROKU","PARA","WBD","FOXA","LYV","IMAX","AMCX","SPOT",
"GOOGL","META","SNAP","PINS","TWTR","BIDU","BABA","JD","PDD","TCEHY",
"SHOP","MELI","SE","GLBE","WIX","SQ","PYPL","AFRM","UPST","SOFI",
"NVDA","AMD","INTC","QCOM","TXN","MU","LRCX","KLAC","AMAT","ASML",
"TSM","GFS","ON","WOLF","MRVL","SWKS","QRVO","AVGO","ADI","NXPI",
"FSLR","ENPH","SEDG","RUN","SPWR","NEE","DUK","SO","AEP","ED",
"XEL","PEG","D","EIX","PCG","SRE","WEC","CMS","ATO","NI",
"BRK.A","BRK.B","MKL","AIG","MET","PRU","LNC","UNM","GL","PFG",
"HIG","ALL","TRV","CB","AFL","PGR","CINF","WRB","RE","RNR",
"SPGI","MSCI","ICE","NDAQ","CME","MCO","FDS","MKTX","TW","BR",
"PANW","CRWD","ZS","FTNT","OKTA","DDOG","SNOW","MDB","NET","SPLK",
"ORCL","SAP","ADBE","CRM","INTU","NOW","TEAM","WDAY","PAYC","MSFT",
"AMZN","SHOP","MELI","SE","WMT","TGT","COST","DG","DLTR","BJ",
"TSLA","RIVN","LCID","NIO","XPEV","LI","F","GM","STLA","HMC",
"BA","LMT","NOC","RTX","GD","TDG","HEI","TXT","SPR","GE",
"XOM","CVX","COP","OXY","PXD","EOG","DVN","FANG","MRO","APA",
"SLB","HAL","BKR","VLO","PSX","MPC","HES","KMI","WMB","OKE",
"JPM","BAC","WFC","C","GS","MS","USB","PNC","TFC","BK",
"V","MA","AXP","DFS","COF","SYF","PYPL","SQ","AFRM","HOOD",
"KO","PEP","MNST","KDP","CELH","STZ","BF.B","TAP","MO","PM",
"PG","CL","KMB","CHD","EL","COTY","IPAR","UL","NKE","LULU",
"HD","LOW","TSCO","WMT","COST","TGT","DG","DLTR","BJ","BBY",
"CAT","DE","CMI","PCAR","OSK","AGCO","PWR","JCI","EMR","ETN",
"MMM","HON","ROK","IR","XYL","AWK","AOS","MAS","FBHS","WHR",
"PLD","AMT","CCI","EQIX","PSA","SPG","O","WELL","VTR","EQR",
"AVB","UDR","ESS","MAA","CPT","ARE","BXP","SLG","VNO","HST",
"LEN","DHI","PHM","TOL","NVR","HD","LOW","TSCO","WMT","COST",
"DIS","NFLX","ROKU","PARA","WBD","FOXA","LYV","IMAX","AMCX","SPOT",
"GOOGL","META","SNAP","PINS","TWTR","BIDU","BABA","JD","PDD","TCEHY"
]
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

    # ترند أقوى: Sma10 < Sma20 < Sma50
    df["Trend"] = (df["Sma10"] < df["Sma20"]) & (df["Sma20"] < df["Sma50"])

    # تأكيد أقوى: إغلاق الغد أعلى من أعلى سعر اليوم
    df["Confirm"] = df["Close"].shift(-1) > df["High"]

    # قوة الشمعة (أكثر تيسيرًا من V2)
    candle_range = df["High"] - df["Low"]
    strong_range = candle_range > 0.30 * df["Atr14"]

    # فلتر تقلبات: نتجنب الفترات الميتة
    df["VolFilter"] = df["Atr14"] > df["Atr14"].rolling(50, min_periods=1).mean()

    # فلتر حماية من الشموع المجنونة
    df["NoSpike"] = (df["High"] - df["Low"]) < df["Atr14"] * 3

    df["Bull"] = spy_bull.reindex(df.index).fillna(False)

    # الإشارة النهائية – Aggressive Enhanced
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
def simulate_trades(df, ticker):
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

       leverage = 3.0  # تقريب لحساسية الأوبشن
ret = ((exit_close - entry_open) / entry_open) * leverage
ret = max(ret, -1.0)  # ما نخلي الخسارة تتعدى -100%


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


# ----------------- باك تست سهم واحد -----------------
def backtest_ticker(ticker, spy_bull):
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

        trades_df = simulate_trades(df, ticker)
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


# ----------------- محفظة كاملة -----------------
def build_portfolio_equity(all_trades_df):
    if all_trades_df.empty:
        return pd.Series(dtype=float)

    all_trades_df = all_trades_df.sort_values("exit_date").copy()
    eq = (1 + all_trades_df["return_pct"] / 100.0).cumprod()
    eq.index = all_trades_df["exit_date"]
    return eq
# ----------------- واجهة Streamlit -----------------
st.set_page_config(page_title="Hammer Backtest – Balanced V2.5 Aggressive", layout="wide")

st.title("Hammer Backtest – Balanced V2.5 – Aggressive Enhanced Edition")
st.write(
    "نسخة Aggressive محسّنة من Balanced V2: عدد صفقات أعلى، عائد تراكمي أعلى، مع الحفاظ على Win Rate قوي."
)

with st.spinner("جاري تحميل بيانات SPY..."):
    spy_regime = load_spy_regime()
st.success("تم تحميل بيانات SPY بنجاح.")

selected_tickers = st.multiselect(
    "اختر الأسهم:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:50],
)

run_button = st.button("ابدأ الباك تست")

if run_button:
    if not selected_tickers:
        st.warning("اختر سهم واحد على الأقل.")
    else:
        st.write("### النتائج لكل سهم")

        all_summaries = []
        all_trades_list = []

        for ticker in selected_tickers:
            st.write("---")
            st.subheader(f"🔍 {ticker}")

            with st.spinner(f"تشغيل الباك تست لـ {ticker}..."):
                result = backtest_ticker(ticker, spy_regime)

            st.write("#### Log")
            st.code(result["log"])

            summary = result["summary"]
            trades_df = result["trades"]
            equity = result["equity"]

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
                row = summary.copy()
                row["ticker"] = ticker
                all_summaries.append(row)

            if not trades_df.empty:
                st.write("#### الصفقات")
                st.dataframe(trades_df)
                all_trades_list.append(trades_df)
            else:
                st.info("لا توجد صفقات.")

            if not equity.empty:
                st.write("#### Equity Curve (سهم واحد)")
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.plot(equity.index, equity.values, label=ticker)
                ax.set_title(f"Equity Curve – {ticker}")
                ax.grid(True, alpha=0.3)
                ax.legend()
                st.pyplot(fig)

        # مقارنة بين الأسهم
        if all_summaries:
            st.write("---")
            st.write("### مقارنة بين الأسهم")
            summary_df = pd.DataFrame(all_summaries).set_index("ticker")
            st.dataframe(summary_df.sort_values("cum_return", ascending=False))

            st.write("#### عائد تراكمي لكل سهم")
            fig_bar, ax_bar = plt.subplots(figsize=(8, 4))
            sorted_df = summary_df.sort_values("cum_return", ascending=False)
            ax_bar.bar(sorted_df.index, sorted_df["cum_return"])
            ax_bar.set_xticklabels(sorted_df.index, rotation=90)
            ax_bar.set_ylabel("Cumulative Return %")
            ax_bar.set_title("Cumulative Return per Stock")
            ax_bar.grid(True, axis="y", alpha=0.3)
            st.pyplot(fig_bar)

        # محفظة كاملة
        if all_trades_list:
            st.write("---")
            st.write("### محفظة كاملة (كل الصفقات من كل الأسهم)")

            portfolio_trades = pd.concat(all_trades_list, ignore_index=True)
            portfolio_equity = build_portfolio_equity(portfolio_trades)

            st.write("#### Equity Curve للمحفظة")
            if not portfolio_equity.empty:
                fig_port, ax_port = plt.subplots(figsize=(8, 4))
                ax_port.plot(portfolio_equity.index, portfolio_equity.values, label="Portfolio")
                ax_port.set_title("Portfolio Equity Curve")
                ax_port.grid(True, alpha=0.3)
                ax_port.legend()
                st.pyplot(fig_port)

            port_summary = summarize_trades(portfolio_trades)
            st.write("#### Summary للمحفظة")
            st.write(
                f"- عدد الصفقات: {port_summary['trades']}\n"
                f"- نسبة الربح: {port_summary['win_rate']:.1f}%\n"
                f"- متوسط العائد: {port_summary['avg_return']:.2f}%\n"
                f"- أكبر ربح: {port_summary['max_gain']:.2f}%\n"
                f"- أكبر خسارة: {port_summary['max_loss']:.2f}%\n"
                f"- العائد التراكمي: {port_summary['cum_return']:.2f}%"
            )

        st.success("تم الانتهاء.")
