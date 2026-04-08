import streamlit as st
import pandas as pd
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.title("Original Hammer Backtest (with FULL LOG)")

if st.button("Run Backtest"):

    spy_bull = load_spy_regime()

    log_output = ""
    all_trades = []

    progress = st.progress(0)

    for i, t in enumerate(LIQUID_TICKERS):

        df = backtest_ticker(t, spy_bull)

        # نضيف لوج كل سهم داخل Streamlit
        log_output += f"{t}: processed\n"

        if df is not None and not df.empty:
            log_output += f"  → trades: {len(df)}\n"
            all_trades.append(df)
        else:
            log_output += f"  → NO TRADES\n"

        progress.progress((i + 1) / len(LIQUID_TICKERS))

    # نعرض اللوج كامل داخل Streamlit
    st.text_area("LOG OUTPUT", log_output, height=400)

    if not all_trades:
        st.error("No trades generated.")
    else:
        trades = pd.concat(all_trades, ignore_index=True)
        st.success(f"Trades generated: {len(trades)}")
        st.dataframe(trades.head(50))
