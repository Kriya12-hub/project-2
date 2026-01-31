import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="ALPHA STACK",
    layout="wide"
)

# ================== HEADER ==================
st.markdown("""
<style>
.header {
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.logo {
    font-weight:800;
    font-size:28px;
}
.tagline {
    font-size:14px;
    color:gray;
}
.marquee {
    font-size:14px;
    color:#0a66c2;
}
</style>

<div class="header">
    <div>
        <div class="logo">ALPHA STACK</div>
        <div class="tagline">Market Intelligence Engine</div>
    </div>
    <div>📊</div>
</div>

<marquee class="marquee">
Investing is about managing risk, not predicting prices • Built by Kriya
</marquee>
""", unsafe_allow_html=True)

st.markdown("---")

# ================== SIDEBAR ==================
st.sidebar.title("Navigation")

section = st.sidebar.radio(
    "",
    [
        "Market Overview",
        "Buy / Sell Decision",
        "Deep Analysis",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Portfolio Risk Checker",
    ]
)

st.sidebar.caption("Built for clarity, not hype")

# ================== INPUT ==================
symbol = st.text_input(
    "Enter Stock Symbol (.NS for India)",
    "RELIANCE.NS"
)

if not symbol:
    st.stop()

# ================== DATA FETCH ==================
stock = yf.Ticker(symbol)
price_data = stock.history(period="3y")

if price_data.empty:
    st.error("Invalid symbol or data unavailable.")
    st.stop()

info = stock.info
financials = stock.financials
balance = stock.balance_sheet
cashflow = stock.cashflow

currency = "₹" if symbol.endswith(".NS") else "$"
price = price_data["Close"].iloc[-1]

# ================== DERIVED METRICS ==================
returns = price_data["Close"].pct_change().dropna()
volatility = returns.std() * 100

# Moving averages
ma50 = price_data["Close"].rolling(50).mean()
ma200 = price_data["Close"].rolling(200).mean()

# Drawdown
cum_max = price_data["Close"].cummax()
drawdown = (price_data["Close"] - cum_max) / cum_max * 100

# CAGR
years = len(price_data) / 252
cagr = (price_data["Close"].iloc[-1] / price_data["Close"].iloc[0]) ** (1/years) - 1

# ROE & ROCE (computed manually)
roe = roce = None

try:
    net_income = financials.loc["Net Income"][0]
    equity = balance.loc["Total Stockholder Equity"][0]
    roe = net_income / equity
except:
    pass

try:
    ebit = financials.loc["Ebit"][0]
    total_assets = balance.loc["Total Assets"][0]
    current_liabilities = balance.loc["Total Current Liabilities"][0]
    capital_employed = total_assets - current_liabilities
    roce = ebit / capital_employed
except:
    pass

# ================== MARKET OVERVIEW ==================
if section == "Market Overview":
    st.subheader("📌 Market Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"{currency}{price:.2f}")
    col2.metric("Annualized Return", f"{cagr*100:.2f}%")
    col3.metric("Volatility", f"{volatility:.2f}%")

    st.line_chart(price_data["Close"])

    st.markdown("""
**How to read this:**  
• Higher volatility = more emotional swings  
• CAGR shows long-term compounding ability  
• Price trend gives market confidence signal
""")

# ================== BUY / SELL DECISION ==================
elif section == "Buy / Sell Decision":
    st.subheader("📌 Buy / Sell / Wait Decision")

    st.line_chart(pd.DataFrame({
        "Price": price_data["Close"],
        "50 DMA": ma50,
        "200 DMA": ma200
    }))

    if price > ma50.iloc[-1] > ma200.iloc[-1]:
        st.success(f"""
**Trend:** Strong  
**Strategy:** Buy only on dips near {currency}{ma50.iloc[-1]:.2f}  
**Exit if:** Price breaks below {currency}{ma200.iloc[-1]:.2f}
""")
    elif price < ma200.iloc[-1]:
        st.error("""
**Trend:** Weak  
**Strategy:** Avoid or exit  
**Reason:** Long-term structure broken
""")
    else:
        st.warning("""
**Trend:** Neutral  
**Strategy:** Wait for clarity  
""")

# ================== DEEP ANALYSIS ==================
elif section == "Deep Analysis":
    st.subheader("📊 Risk & Behavioural Analysis")

    st.markdown("### Drawdown Analysis")
    st.line_chart(drawdown)

    st.markdown("""
This chart shows **worst historical pain** from peaks.
It answers: *Can you hold this stock during crashes?*
""")

    st.markdown("### Return Distribution")
    st.bar_chart(returns * 100)

# ================== FUNDAMENTALS ==================
elif section == "Fundamentals Decoder":
    st.subheader("📘 Fundamentals Decoder")

    data = {
        "Market Cap": info.get("marketCap"),
        "P/E Ratio": info.get("trailingPE"),
        "Debt to Equity": info.get("debtToEquity"),
        "ROE": roe,
        "ROCE": roce,
        "Profit Margin": info.get("profitMargins"),
        "Dividend Yield": info.get("dividendYield"),
    }

    df = pd.DataFrame.from_dict(data, orient="index", columns=["Value"])
    st.table(df)

    if roe and roe > 0.15:
        st.success("Strong capital efficiency.")
    else:
        st.warning("Capital efficiency is average or weak.")

# ================== FINANCIAL HEALTH ==================
elif section == "Financial Health (Beginner)":
    st.subheader("🩺 Financial Health — Simple Language")

    if not cashflow.empty:
        cfo = cashflow.loc["Total Cash From Operating Activities"]
        st.line_chart(cfo)

        if cfo.mean() > 0:
            st.success("Company generates real operating cash.")
        else:
            st.error("Cash generation is weak.")
    else:
        st.warning("Cash flow data unavailable.")

    st.markdown("""
**Beginner Verdict:**  
Strong businesses generate cash consistently.
""")

# ================== PORTFOLIO RISK ==================
elif section == "Portfolio Risk Checker":
    st.subheader("⚠️ Portfolio Risk Checker")

    amount = st.number_input("Investment Amount (₹)", 50000)
    stocks = st.slider("Number of stocks in portfolio", 1, 20, 5)
    risk = st.selectbox("Risk Profile", ["Low", "Medium", "High"])

    if stocks < 5:
        st.error("High concentration risk.")
    else:
        st.success("Diversification acceptable.")

    if volatility > 2.5 and risk == "Low":
        st.error("Stock volatility mismatches your risk profile.")
    else:
        st.success("Risk alignment reasonable.")

# ================== FOOTER ==================
st.markdown("---")
st.caption("Alpha Stack • Built for decision-making, not speculation • Made by Kriya")
