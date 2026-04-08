import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest – Diagnostics", layout="wide")

st.title("Hammer Backtest – التشخيص الكامل")
st.write("يعرض هذا النظام نتائج الباك تست بالتفصيل لكل سهم تقوم باختياره من القائمة.")

# Load SPY regime once
with st.spinner("جاري تحميل بيانات SPY..."):
    spy_regime = load_spy_regime()
st.success("تم تحميل بيانات SPY بنجاح.")

# Ticker selection
selected_tickers = st.multiselect(
    "اختر الأسهم التي تريد اختبارها:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:10],
)

run_button = st.button("ابدأ الباك تست")

if run_button:
    if not selected_tickers:
        st.warning("الرجاء اختيار سهم واحد على الأقل.")
    else:
        st.write("### النتائج الكاملة لكل سهم")

        for ticker in selected_tickers:
            st.write("---")
            st.subheader(f"🔍 {ticker} – Full Diagnostics")

            with st.spinner(f"جاري تشغيل الباك تست لـ {ticker}..."):
                result = backtest_ticker(ticker, spy_regime)

            st.write("#### Raw Output (Text)")
            st.code(str(result))

        st.success("تم الانتهاء من جميع الاختبارات.")
