import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.title("FULL DIAGNOSTIC BACKTEST")

if st.button("Run Diagnostics"):
    spy_bull = load_spy_regime()

    full_log = ""

    for t in LIQUID_TICKERS:
        result = backtest_ticker(t, spy_bull)
        full_log += result + "\n"

    st.text_area("LOG", full_log, height=600)
