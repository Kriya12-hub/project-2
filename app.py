import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.title("ALPHA STACK")
section = st.sidebar.radio(
    "Navigation",
    [
        "Market Overview",
        "Buy / Sell Decision",
        "Deep Analysis",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Sentiment & News Intelligence",
        "Confidence Score",
        "Portfolio Risk Checker",
        "Compare Two Stocks",
        "Long-Term Wealth"
    ]
)

# ---------- HEADER ----------
st.title("Turn Data into Conviction.")
st.caption("Markets explained. Decisions simplified.")

symbol = st.text_input("Enter Stock Symbol (.NS for India)", "RELIANCE.NS")

if not symbol:
    st.stop()

stock = yf.Ticker(symbol)
data = stock.history(period="1y")

if data.empty:
    st.error("Invalid symbol or no data available.")
    st.stop()

info = stock.info
currency = "₹" if symbol.endswith(".NS") else "$"

price = data["Close"].iloc[-1]
prev = data["Close"].iloc[-2]
change_pct = ((price - prev) / prev) * 100

# ---------- HELPERS ----------
def market_cap_simple(val):
    if not val:
        return "N/A"
    return f"₹{val/1e7:,.0f} Cr"

daily_returns = data["Close"].pct_change().dropna()
volatility = daily_returns.std() * 100

ma50 = data["Close"].rolling(50).mean().iloc[-1]
ma200 = data["Close"].rolling(200).mean().iloc[-1]

# ---------- CONFIDENCE SCORE ----------
score = 0

# Trend
if price > ma50 > ma200:
    score += 25
elif price > ma50:
    score += 15

# Volatility
if volatility < 1.2:
    score += 20
elif volatility < 2.5:
    score += 10

# Valuation
pe = info.get("trailingPE")
if pe and pe < 20:
    score += 20
elif pe:
    score += 10

# Profitability
margin = info.get("profitMargins")
if margin and margin > 0.15:
    score += 20
elif margin:
    score += 10

# Cash flow
cfo = info.get("operatingCashflow")
if cfo and cfo > 0:
    score += 15

# ======================================================
if section == "Market Overview":
    st.metric("Price", f"{currency}{price:.2f}", f"{change_pct:.2f}%")
    st.write(f"**Confidence Score:** {score}/100")
    st.line_chart(data["Close"])
    st.write(info.get("longBusinessSummary", ""))

# ======================================================
elif section == "Buy / Sell Decision":
    st.subheader("Action Zones (Not Predictions)")
    st.write(f"Buy Zone: near {currency}{ma50:.2f}")
    st.write(f"Sell / Risk Zone: below {currency}{ma200:.2f}")

# ======================================================
elif section == "Deep Analysis":
    st.line_chart(data["Close"])
    rolling = data["Close"].pct_change(30) * 100
    st.line_chart(rolling)

# ======================================================
elif section == "Fundamentals Decoder":
    st.table(pd.DataFrame({
        "Metric": ["Market Cap", "P/E", "ROE", "Debt to Equity"],
        "Value": [
            market_cap_simple(info.get("marketCap")),
            pe,
            info.get("returnOnEquity"),
            info.get("debtToEquity")
        ]
    }))

# ======================================================
elif section == "Financial Health (Beginner)":
    st.write("Cash Flow:", "Positive" if cfo and cfo > 0 else "Negative")
    st.write("Profit Margins:", "Healthy" if margin and margin > 0.15 else "Weak")

# ======================================================
elif section == "Sentiment & News Intelligence":
    for n in stock.news[:5]:
        st.markdown(f"**[{n['title']}]({n['link']})**")
        st.caption(n.get("publisher", ""))

# ======================================================
elif section == "Confidence Score":
    st.metric("Alpha Stack Confidence Score", f"{score}/100")
    if score >= 80:
        st.success("Strong candidate for disciplined investors.")
    elif score >= 60:
        st.warning("Decent stock, timing matters.")
    else:
        st.error("High risk for beginners.")

# ======================================================
elif section == "Portfolio Risk Checker":
    amount = st.number_input("Investment Amount (₹)", 10000)
    stocks = st.number_input("No. of stocks in portfolio", 1)
    risk = st.selectbox("Risk Appetite", ["Low", "Medium", "High"])

    if stocks < 5 and risk == "Low":
        st.error("High concentration risk for low-risk investor.")
    else:
        st.info("Portfolio risk seems aligned.")

# ======================================================
elif section == "Compare Two Stocks":
    sym2 = st.text_input("Second Stock Symbol", "TCS.NS")
    s2 = yf.Ticker(sym2)
    d2 = s2.history(period="1y")

    if not d2.empty:
        st.write("### Comparison")
        st.table(pd.DataFrame({
            "Metric": ["Price", "Volatility"],
            symbol: [price, volatility],
            sym2: [d2["Close"].iloc[-1], d2["Close"].pct_change().std()*100]
        }))

# ======================================================
elif section == "Long-Term Wealth":
    if score >= 70:
        st.success("Suitable for long-term holding with patience.")
    else:
        st.warning("Wait or invest cautiously.")

st.markdown("---")
st.caption("Made by Kriya Chhajed")
