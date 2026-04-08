import streamlit as st
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.set_page_config(page_title="Hammer Backtest – Diagnostics", layout="wide")

st.title("Hammer Backtest – Full Diagnostics")
st.write("يعرض لوج كامل لكل سهم: ه