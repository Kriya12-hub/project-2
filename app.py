import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("ALPHA STACK")
section = st.sidebar.radio(
    "Navigation",
    [
        "Buy / Sell Decision",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Portfolio Simulation",
        "Monte Carlo Simulation"
    ]
)

symbol = st.sidebar.text_input("Enter Stock Symbol (.NS for India)", "RELIANCE.NS")

# ---------------- DATA ----------------
@st.cache_data
def load_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="5y")
    info = stock.info
    return hist, info, stock

price_data, info, stock = load_data(symbol)

current_price = price_data["Close"].iloc[-1]

# ================= BUY / SELL =================
if section == "Buy / Sell Decision":
    st.title("📌 Buy / Sell Decision")

    ma50 = price_data["Close"].rolling(50).mean().iloc[-1]
    ma200 = price_data["Close"].rolling(200).mean().iloc[-1]

    st.metric("Current Price", f"₹{current_price:,.0f}")
    st.metric("50 DMA", f"₹{ma50:,.0f}")
    st.metric("200 DMA", f"₹{ma200:,.0f}")

    if current_price > ma50 > ma200:
        st.success("✅ TREND: Strong Uptrend")
        st.markdown("""
**Verdict:**  
• Long-term investors can accumulate on dips  
• Short-term traders should buy near 50 DMA  
• Stop-loss: Below 200 DMA  
""")
    elif current_price < ma50 < ma200:
        st.error("❌ TREND: Downtrend")
        st.markdown("""
**Verdict:**  
• Avoid fresh buying  
• Existing investors should protect capital  
""")
    else:
        st.warning("⚠️ TREND: Sideways / Unclear")
        st.markdown("""
**Verdict:**  
• Wait for confirmation  
• Risk-reward not attractive right now  
""")

# ================= FUNDAMENTALS =================
elif section == "Fundamentals Decoder":
    st.title("📘 Fundamentals Decoder")

    def show(label, value):
        st.metric(label, value if value else "Data unavailable")

    col1, col2, col3 = st.columns(3)

    with col1:
        show("Market Cap", f"₹{info.get('marketCap',0)/1e7:.0f} Cr")
        show("P/E Ratio", info.get("trailingPE"))
        show("Book Value", info.get("bookValue"))

    with col2:
        show("ROE (%)", info.get("returnOnEquity"))
        show("Debt to Equity", info.get("debtToEquity"))
        show("Dividend Yield", info.get("dividendYield"))

    with col3:
        show("52W High", info.get("fiftyTwoWeekHigh"))
        show("52W Low", info.get("fiftyTwoWeekLow"))
        show("Industry", info.get("industry"))

    st.markdown("""
### 🧠 Interpretation
• High ROE = efficient business  
• High Debt = risk during downturns  
• P/E too high = future growth already priced in  
""")

# ================= FINANCIAL HEALTH =================
elif section == "Financial Health (Beginner)":
    st.title("💊 Financial Health (Simple Language)")

    cashflow = stock.cashflow

    if cashflow.empty:
        st.warning("Cash flow data not available.")
    else:
        cfo = cashflow.iloc[0].sum()
        if cfo > 0:
            st.success("✅ Company generates positive operating cash")
        else:
            st.error("❌ Company struggles to generate cash")

    st.markdown("""
### Beginner Verdict
• Cash-generating businesses survive crises  
• Profit without cash is dangerous  
""")

# ================= PORTFOLIO SIM =================
elif section == "Portfolio Simulation":
    st.title("📈 Portfolio Simulation")

    amount = st.number_input("Investment Amount (₹)", 10000, value=100000)
    years = st.slider("Years", 1, 10, 3)

    prices = price_data["Close"].tail(years * 252)
    units = amount / prices.iloc[0]
    portfolio = units * prices

    cagr = ((portfolio.iloc[-1] / amount) ** (1/years) - 1) * 100
    drawdown = (portfolio / portfolio.cummax() - 1).min() * 100

    st.line_chart(portfolio)

    st.metric("Final Value", f"₹{portfolio.iloc[-1]:,.0f}")
    st.metric("CAGR", f"{cagr:.2f}%")
    st.metric("Max Drawdown", f"{drawdown:.2f}%")

    st.markdown("""
### 🧠 What this tells you
• Can you tolerate this drawdown emotionally?  
• Returns mean nothing if risk is unbearable  
""")

# ================= MONTE CARLO =================
elif section == "Monte Carlo Simulation":
    st.title("🔮 Monte Carlo Simulation")

    returns = np.log(price_data["Close"] / price_data["Close"].shift(1)).dropna()
    mu, sigma = returns.mean(), returns.std()

    days = 252 * 3
    simulations = 500
    paths = np.zeros((days, simulations))
    paths[0] = current_price

    for t in range(1, days):
        paths[t] = paths[t-1] * np.exp(mu + sigma * np.random.randn(simulations))

    st.line_chart(paths[:, :50])

    st.markdown("""
### 🧠 Conclusion
• This is NOT prediction  
• It shows probability, not certainty  
• If worst-case scares you → reduce position size  
""")

st.markdown("---")
st.caption("Made by Kriya • Investing is risk management, not prediction")
