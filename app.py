import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest – Diagnostics", layout="wide")

st.title("Hammer Backtest – Full Diagnostics")
st.write("يعرض لوج كامل لكل سهم: هنا يمكنك رؤية نتائج الباك تست بالتفصيل لكل سهم في القائمة.")

# Load SPY regime once
st.sidebar.header("Settings")
st.sidebar.write("يتم تحميل نظام SPY مرة واحدة لتسريع العملية.")

with st.spinner("Loading SPY regime..."):
    spy_regime = load_spy_regime()

st.success("SPY regime loaded successfully.")

# User selects tickers
selected_tickers = st.multiselect(
    "اختر الأسهم التي تريد اختبارها:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:10]  # show first 10 by default
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

            with st.spinner(f"Running backtest for {ticker}..."):
                try:
                    result = backtest_ticker(ticker, spy_regime)
                except Exception as e:
                    st.error(f"Error while backtesting {ticker}: {e}")
                    continue

            # Expecting result to contain:
            # result["summary"], result["log"], result["plot"], result["stats"]
            # Adjust based on your actual backtester output.

            # Summary
            if "summary" in result:
                st.write("#### Summary")
                st.json(result["summary"])

            # Stats
            if "stats" in result:
                st.write("#### Performance Stats")
                st.json(result["stats"])

            # Plot
            if "plot" in result:
                st.write("#### Equity Curve")
                st.pyplot(result["plot"])

            # Log
            if "log" in result:
                with st.expander("📄 Full Log"):
                    st.text(result["log"])

        st.success("تم الانتهاء من جميع الاختبارات.")
