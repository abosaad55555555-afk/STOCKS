import streamlit as stimport streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest ñ Diagnostics", layout="wide")

st.title("Hammer Backtest ñ Full Diagnostics")
st.write("Ì⁄—÷ ·ÊÃ ﬂ«„· ·ﬂ· ”Â„: Â‰« Ì„ﬂ‰ﬂ —ƒÌ… ‰ «∆Ã «·»«ﬂ  ”  »«· ›’Ì· ·ﬂ· ”Â„ ›Ì «·ﬁ«∆„….")

# Load SPY regime
with st.spinner("Loading SPY regime..."):
    spy_regime = load_spy_regime()
st.success("SPY regime loaded successfully.")

# Select tickers
selected_tickers = st.multiselect(
    "«Œ — «·√”Â„ «· Ì  —Ìœ «Œ »«—Â«:",
    LIQUID_TICKERS,
    default=LIQUID_TICKERS[:10]
)

run_button = st.button("«»œ√ «·»«ﬂ  ” ")

if run_button:
    if not selected_tickers:
        st.warning("«·—Ã«¡ «Œ Ì«— ”Â„ Ê«Õœ ⁄·Ï «·√ﬁ·.")
    else:
        st.write("### «·‰ «∆Ã «·ﬂ«„·… ·ﬂ· ”Â„")

        for ticker in selected_tickers:
            st.write("---")
            st.subheader(f"?? {ticker} ñ Full Diagnostics")

            with st.spinner(f"Running backtest for {ticker}..."):
                try:
                    result = backtest_ticker(ticker, spy_regime)
                except Exception as e:
                    st.error(f"Error while backtesting {ticker}: {e}")
                    continue

            # ALWAYS show raw output as text
            st.write("#### Raw Output (Text)")
            st.code(str(result))

            # If result is dict, show details
            if isinstance(result, dict):
                for key, value in result.items():
                    with st.expander(f"{key}"):
                        st.write(value)

        st.success(" „ «·«‰ Â«¡ „‰ Ã„Ì⁄ «·«Œ »«—« .")
