import streamlit as st
import pandas as pd
from tickers import LIQUID_TICKERS
from backtester import backtest_ticker, load_spy_regime

st.title("Minimal Backtester – Sanity Check")
st.write("هذا الإصدار هدفه الوحيد: التأكد إن في بيانات وإن في صفقات فعلاً.")

if st.button("Run Backtest"):

    with st.spinner("Loading SPY regime (not used in signal logic)..."):
        spy_bull = load_spy_regime()

    all_trades = []
    progress = st.progress(0)

    for i, t in enumerate(LIQUID_TICKERS):
        df = backtest_ticker(t, spy_bull)
        if df is not None and not df.empty:
            all_trades.append(df)
        progress.progress((i + 1) / len(LIQUID_TICKERS))

    if not all_trades:
        st.error("No trades generated. هذا يعني غالباً أن بيانات yfinance فاضية أو فيها مشكلة شبكة.")
    else:
        trades = pd.concat(all_trades, ignore_index=True)
        st.success(f"Trades generated: {len(trades)}")

        st.write("### Sample trades")
        st.dataframe(trades.head(50))

        st.write("### Summary")
        st.write("Win rate:", float((trades["OptionReturn"] > 0).mean()))
        st.write("Avg option return:", float(trades["OptionReturn"].mean()))

        csv = trades.to_csv(index=False)
        st.download_button(
            "Download trades CSV",
            csv,
            "hammer_trades_sanity.csv",
            "text/csv"
        )
