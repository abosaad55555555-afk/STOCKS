import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest – Diagnostics", layout="wide")

# Title & description
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
    default=LIQUID_TICKERS[:10]
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

            # Run backtest
            with st.spinner(f"جاري تشغيل الباك تست لـ {ticker}..."):
                try:
                    result = backtest_ticker(ticker, spy_regime)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء اختبار {ticker}: {e}")
                    continue

            # Show raw output
            st.write("#### Raw Output (Text)")
            safe_text = str(result)
            st.code(safe_text)

            # If result is a dict, show its fields
            if isinstance(result, dict):
                for key, value in result.items():
                    with st.expander(str(key)):
                        st.write(value)

        st.success("تم الانتهاء من جميع الاختبارات.")
