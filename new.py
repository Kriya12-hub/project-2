app.py

import streamlit as st
import yfinance as yf
import pandas as pd

# Page config
st.set_page_config(
    page_title="ALPHA STACK",
    layout="wide"
)

# Sidebar
st.sidebar.title("ALPHA STACK")
section = st.sidebar.radio(
    "Navigation",
    [
        "Market Sentiment",
        "Deep Analysis",
        "Chart Lab",
        "Fundamentals Decoder",
        "Trade Scenarios",
        "Long-Term Wealth"
    ]
)

# Header
st.title("Turn Data into Conviction.")
st.caption("Markets explained. Decisions simplified.")

# Stock input
symbol = st.text_input("Enter Stock Symbol", "AAPL")

if symbol:
    stock = yf.Ticker(symbol)
    data = stock.history(period="7d")

    if not data.empty:
        price = data["Close"][-1]
        prev_price = data["Close"][-2]
        change_pct = ((price - prev_price) / prev_price) * 100

        col1, col2, col3, col4 = st.columns(4)

        # Live Price
        col1.metric(
            "Live Price",
            f"${price:.2f}",
            f"{change_pct:.2f}%"
        )

        # Market Sentiment
        if change_pct > 1:
            sentiment = "Bullish momentum with active participation"
        elif change_pct < -1:
            sentiment = "Bearish pressure with distribution signals"
        else:
            sentiment = "Neutral regime with balanced forces"

        col2.subheader("Market Sentiment")
        col2.write(sentiment)

        # Fundamentals
        info = stock.info
        col3.subheader("Fundamentals Snapshot")
        col3.write(f"Market Cap: {info.get('marketCap', 'N/A')}")
        col3.write(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")
        col3.write(f"ROE: {info.get('returnOnEquity', 'N/A')}")

        # Trade Scenario
        col4.subheader("Trade Scenario")
        col4.write(
            "Base case favors consolidation unless volume confirms expansion."
        )

        # Chart
        st.subheader("Price Structure")
        st.line_chart(data["Close"])

    else:
        st.error("Invalid symbol or no data available")

# Footer
st.markdown("---")
st.caption("Made by Kriya Chhajed")
