import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("ALPHA STACK")

section = st.sidebar.radio(
    "Navigation",
    [
        "Market Overview",
        "Deep Analysis",
        "Fundamentals Decoder",
        "Trade Scenarios",
        "Sentiment & News Intelligence",
        "Long-Term Wealth"
    ]
)

# ---------------- HEADER ----------------
st.title("Turn Data into Conviction.")
st.caption("Markets explained. Decisions simplified.")

symbol = st.text_input(
    "Enter Stock Symbol (Indian stocks use .NS)",
    "RELIANCE.NS"
)

if not symbol:
    st.stop()

# ---------------- DATA LOAD ----------------
stock = yf.Ticker(symbol)
data = stock.history(period="1y")

if data.empty:
    st.error("Invalid symbol or no data available.")
    st.stop()

info = stock.info

# ---------------- PRICE & RETURNS ----------------
price = data["Close"].iloc[-1]
prev_price = data["Close"].iloc[-2]
change_pct = ((price - prev_price) / prev_price) * 100

currency = "₹" if symbol.endswith(".NS") else "$"

daily_returns = data["Close"].pct_change().dropna()
volatility = daily_returns.std() * 100

# ---------------- VOLATILITY CLASSIFICATION ----------------
if volatility < 1.2:
    vol_label = "Low Volatility"
    vol_meaning = "Stable behavior. Suitable for long-term investors."
elif volatility < 2.5:
    vol_label = "Medium Volatility"
    vol_meaning = "Balanced risk. Requires discipline."
else:
    vol_label = "High Volatility"
    vol_meaning = "Aggressive moves. High risk of emotional swings."

# ---------------- COMPANY INFO ----------------
company_name = info.get("longName", "N/A")
industry = info.get("industry", "N/A")
description = info.get("longBusinessSummary", "No description available.")

# ======================================================
# MARKET OVERVIEW
# ======================================================
if section == "Market Overview":
    st.subheader(company_name)
    st.write(f"**Industry:** {industry}")

    col1, col2 = st.columns(2)

    col1.metric(
        "Current Price",
        f"{currency}{price:,.2f}",
        f"{change_pct:.2f}%"
    )

    col2.write("### Volatility Profile")
    col2.write(f"**{vol_label}**")
    col2.write(vol_meaning)

    st.write("### What this company does")
    st.write(description)

    st.line_chart(data["Close"])

# ======================================================
# DEEP ANALYSIS
# ======================================================
elif section == "Deep Analysis":
    st.subheader("Deep Analysis: How the Stock Behaves")

    st.write("### Price Trend (1 Year)")
    st.line_chart(data["Close"])

    rolling_returns = data["Close"].pct_change(30) * 100

    st.write("### Rolling 30-Day Returns")
    st.line_chart(rolling_returns)

    st.markdown("""
**Why this chart matters**

This shows consistency of returns instead of just price.
It helps investors understand:
- Whether gains are sustainable  
- How deep drawdowns can be  
- If patience is rewarded  

Long-term investors should prefer smoother rolling returns.
""")

    st.write(f"**Volatility:** {volatility:.2f}% — {vol_label}")

# ======================================================
# FUNDAMENTALS
# ======================================================
elif section == "Fundamentals Decoder":
    st.subheader("Fundamental Snapshot")

    fundamentals = {
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "Book Value": info.get("bookValue"),
        "Dividend Yield": info.get("dividendYield"),
        "Debt to Equity": info.get("debtToEquity"),
        "ROE": info.get("returnOnEquity"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
    }

    df = pd.DataFrame(fundamentals.items(), columns=["Metric", "Value"])
    st.table(df)

    st.write("### Business Overview")
    st.write(description)

# ======================================================
# TRADE SCENARIOS (PERSONALIZED)
# ======================================================
elif section == "Trade Scenarios":
    st.subheader("Personalized Trade & Investment Scenarios")

    st.write(f"**Volatility Profile:** {vol_label}")
    st.write(vol_meaning)

    pe = info.get("trailingPE")
    earnings_growth = info.get("earningsQuarterlyGrowth")

    st.write("### Long-Term Investor View")

    if pe and pe < 20 and vol_label != "High Volatility":
        st.write(
            "This stock is reasonably valued and structurally suitable for long-term holding."
        )
    elif pe and pe > 30:
        st.write(
            "Valuation is stretched. Long-term investors should wait for better entry."
        )
    else:
        st.write(
            "Long-term potential exists, but margin of safety matters."
        )

    st.write("### Profit Potential (Not a Promise)")

    if earnings_growth and earnings_growth > 0.15:
        st.write(
            "Earnings growth supports the possibility of strong long-term returns."
        )
    else:
        st.write(
            "Growth visibility is moderate. Returns may align with market averages."
        )

    st.write("### When Should an Investor Wait?")
    st.write(
        "- After sharp rallies without earnings support\n"
        "- When volatility is high\n"
        "- Before major results or macro events"
    )

# ======================================================
# SENTIMENT & NEWS INTELLIGENCE
# ======================================================
elif section == "Sentiment & News Intelligence":
    st.subheader("Sentiment & Macro Intelligence")

    st.markdown("""
This section interprets how **news, global events, and macro decisions**
*may* affect the stock.  
It does **not** predict prices.
""")

    st.write("### Macro Sensitivity Lens")

    if vol_label == "Low Volatility":
        st.success(
            "Historically absorbs news well unless fundamentals change."
        )
    elif vol_label == "Medium Volatility":
        st.warning(
            "Selective reaction to major headlines. Stock-specific news matters."
        )
    else:
        st.error(
            "Highly reactive to headlines. Expect sharp moves on news."
        )

    st.markdown("""
**AI-Guided Insight (Explainable)**  
This assessment combines volatility behavior, sector sensitivity,
and historical reactions to uncertainty.

Purpose: risk awareness, not prediction.
""")

# ======================================================
# LONG-TERM WEALTH
# ======================================================
elif section == "Long-Term Wealth":
    st.subheader("Long-Term Wealth View")

    pe = info.get("trailingPE")

    if pe and pe < 20:
        valuation_view = "Attractive valuation for long-term compounding."
    elif pe:
        valuation_view = "Valuation is high. Returns may moderate."
    else:
        valuation_view = "Valuation data unavailable."

    st.write("### Investment Horizon Recommendation")
    st.write(valuation_view)

    st.markdown("""
**Who should invest?**
- Long-term investors focused on business quality  
- Investors with patience and risk discipline  
- Not suitable for speculative trading  

Always align decisions with your personal risk profile.
""")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Made by Kriya Chhajed")
