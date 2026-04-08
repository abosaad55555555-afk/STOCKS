import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Hammer Backtest – Diagnostics", layout="wide")

st.title("Hammer Backtest – Full Diagnostics")
st.write("يعرض لوج كامل لكل سهم: هنا يمكنك رؤية نتائج الباك تست بالتفصيل لكل سهم في القائمة.")

# Load SPY regime
with st.spinner("Loading SPY regime..."):
    spy_regime = load_spy_regime()
st.success("SPY regime loaded successfully.")

# Select tickers
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

            with st.spinner(f"Running backtest for {ticker}..."):
                try:
                    result = backtest_ticker(ticker, spy_regime)
                except Exception as e:
                    st.error(f"Error while backtesting {ticker}: {e}")
                    continue

            # Show raw result structure
            st.write("#### Raw Output (Structure)")
            st.json(result)

            # Try to show logs if exist
            if isinstance(result, dict):
                for key, value in result.items():

                    # Show text logs
                    if isinstance(value, str):
                        with st.expander(f"📄 {key} (text)"):
                            st.text(value)

                    # Show numeric tables
                    elif isinstance(value, (list, tuple)):
                        with st.expander(f"📊 {key} (list)"):
                            st.write(value)

                    # Show nested dicts
                    elif isinstance(value, dict):
                        with st.expander(f"📁 {key} (dictionary)"):
                            st.json(value)

                    # Show plots if matplotlib figure
                    elif "Figure" in str(type(value)):
                        st.write(f"📈 {key} (plot)")
                        st.pyplot(value)

                    # Fallback for unknown types
                    else:
                        with st.expander(f"🔧 {key} (other type)"):
                            st.write(value)

        st.success("تم الانتهاء من جميع الاختبارات.")
