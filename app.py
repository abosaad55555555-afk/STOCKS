import streamlit as st
import pandas as pd
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.title("Hammer Pattern Options Backtester")

st.write("Fast, stable, Streamlit‑optimized version.")

spy_bull = load_spy_regime()

if st.button("Run Backtest"):
    all_trades = []

    progress = st.progress(0)
    for i, t in enumerate(LIQUID_TICKERS):
        df = backtest_ticker(t, spy_bull)
        if df is not None:
            all_trades.append(df)
        progress.progress((i+1)/len(LIQUID_TICKERS))

    if not all_trades:
        st.error("No trades generated.")
    else:
        trades = pd.concat(all_trades, ignore_index=True)
        st.success(f"Trades generated: {len(trades)}")

        st.dataframe(trades.head())

        st.write("### Summary")
        st.write("Win rate:", (trades["OptionReturn"]>0).mean())
        st.write("Avg option return:", trades["OptionReturn"].mean())

        st.download_button(
            "Download Trades CSV",
            trades.to_csv(index=False),
            "trades.csv",
            "text/csv"
        )
