import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.title("ALPHA STACK")

section = st.sidebar.radio(
    "Navigation",
    [
        "Market Sentiment",
        "Deep Analysis",
        "Fundamentals Decoder",
        "Trade Scenarios",
        "Long-Term Wealth"
    ]
)

# ---------- HEADER ----------
st.title("Turn Data into Conviction.")
st.caption("Markets explained. Decisions simplified.")

symbol = st.text_input(
    "Enter Stock Symbol (use .NS for Indian stocks)",
    "RELIANCE.NS"
)

if not symbol:
    st.stop()

stock = yf.Ticker(symbol)
data = stock.history(period="1y")

if data.empty:
    st.error("Invalid symbol or no data available.")
    st.stop()

# ---------- PRICE (INR FIX) ----------
price = data["Close"].iloc[-1]
prev = data["Close"].iloc[-2]
change_pct = ((price - prev) / prev) * 100

currency = "₹" if symbol.endswith(".NS") else "$"

# ---------- COMPANY INFO ----------
info = stock.info

company_name = info.get("longName", "N/A")
industry = info.get("industry", "N/A")
description = info.get("longBusinessSummary", "No description available.")

# ==============================
# SECTION 1: MARKET SENTIMENT
# ==============================
if section == "Market Sentiment":
    st.subheader(company_name)
    st.write(f"**Industry:** {industry}")

    col1, col2 = st.columns(2)
    col1.metric(
        "Current Price",
        f"{currency}{price:,.2f}",
        f"{change_pct:.2f}%"
    )

    if change_pct > 1:
        sentiment = "Bullish momentum with strong participation"
    elif change_pct < -1:
        sentiment = "Bearish pressure with selling dominance"
    else:
        sentiment = "Neutral regime, market undecided"

    col2.write("### Sentiment Analysis")
    col2.write(sentiment)

    st.line_chart(data["Close"])

# ==============================
# SECTION 2: DEEP ANALYSIS
# ==============================
elif section == "Deep Analysis":
    st.subheader("Price Behavior & Reliability")

    st.write("### Historical Price Trend")
    st.line_chart(data["Close"])

    st.write("### Volume Analysis")
    st.bar_chart(data["Volume"])

    st.write("### Price Distribution (Volatility)")
    st.bar_chart(data["Close"].value_counts().sort_index())

    volatility = data["Close"].pct_change().std() * 100
    st.write(f"**Volatility:** {volatility:.2f}%")

    if volatility < 1.5:
        st.write("This stock is relatively stable.")
    else:
        st.write("This stock shows high price fluctuations.")

# ==============================
# SECTION 3: FUNDAMENTALS
# ==============================
elif section == "Fundamentals Decoder":
    st.subheader("Fundamental Indicators")

    fundamentals = {
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "Book Value": info.get("bookValue"),
        "Dividend Yield": info.get("dividendYield"),
        "Debt to Equity": info.get("debtToEquity"),
        "ROE": info.get("returnOnEquity"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow")
    }

    df = pd.DataFrame(
        fundamentals.items(),
        columns=["Metric", "Value"]
    )

    st.table(df)

    st.write("### About the Company")
    st.write(description)

# ==============================
# SECTION 4: TRADE SCENARIOS
# ==============================
elif section == "Trade Scenarios":
    st.subheader("Scenario Planning")

    st.write("**Short-Term:**")
    st.write("Depends on momentum and volatility. Suitable only if risk appetite is high.")

    st.write("**Medium-Term:**")
    st.write("Works if fundamentals remain stable and earnings growth continues.")

    st.write("**Invalidation Logic:**")
    st.write("If price breaks below recent support with volume, scenario fails.")

# ==============================
# SECTION 5: LONG-TERM WEALTH
# ==============================
elif section == "Long-Term Wealth":
    st.subheader("Long-Term Investment View")

    pe = info.get("trailingPE")

    if pe and pe < 20:
        valuation_view = "Reasonably valued for long-term holding."
    elif pe:
        valuation_view = "Valuation is stretched; expect lower future returns."
    else:
        valuation_view = "Valuation data unavailable."

    st.write("### Investment Horizon Recommendation")
    st.write(valuation_view)

    st.write("### Who Should Invest?")
    st.write(
        "- Long-term investors focused on business quality\n"
        "- Not ideal for speculative short-term trading\n"
        Note: Always align with your personal risk profile."
    )

# ---------- FOOTER ----------
st.markdown("---")
st.caption("Made by Kriya Chhajed")
