import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest ñ Diagnostics", layout="wide")

st.title("Hammer Backtest ñ Full Diagnostics")
st.write("Ì⁄—÷ ·ÊÃ ﬂ«„· ·ﬂ· ”Â„: Â‰« Ì„ﬂ‰ﬂ —ƒÌ… ‰ «∆Ã «·»«ﬂ  ”  »«· ›’Ì· ·ﬂ· ”Â„ ›Ì «·ﬁ«∆„….")

# Load SPY regime once
with st.spinner("Loading SPY regime..."):
    spy_regime = load_spy_regime()
st.success("SPY regime loaded successfully.")

# Ticker selection
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

            # Run backtest
            with st.spinner(f"Running backtest for {ticker}..."):
                try:
                    result = backtest_ticker(ticker, spy_regime)
                except Exception as e:
                    st.error(f"Error while backtesting {ticker}: {e}")
                    continue

            # Always show raw output as text, with safe encoding
            st.write("#### Raw Output (Text)")
            try:
                # Handle Windows-1252 / Latin-1 style bytes safely
                safe_text = str(result).encode("latin-1", "ignore").decode("utf-8", "ignore")
            except Exception:
                safe_text = str(result)

            st.code(safe_text)

            # If result is a dict, show its fields in expanders
            if isinstance(result, dict):
                for key, value in result.items():
                    with st.expander(str(key)):
                        st.write(value)

        st.success(" „ «·«‰ Â«¡ „‰ Ã„Ì⁄ «·«Œ »«—« .")
