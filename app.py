import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ================== CONFIG ==================
st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ================== SIDEBAR ==================
st.sidebar.title("ALPHA STACK")

section = st.sidebar.radio(
    "Navigation",
    [
        "Buy / Sell Decision",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Portfolio Risk Checker",
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Built for clarity, not hype")

# ================== HEADER ==================
st.title("Turn Data into Conviction.")
st.caption("Markets explained. Decisions simplified.")

symbol = st.text_input("Enter Stock Symbol (.NS for India)", "RELIANCE.NS")

if not symbol:
    st.stop()

# ================== DATA ==================
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

# ================== HELPERS ==================
def cr(val):
    if not val:
        return "N/A"
    return f"₹{val/1e7:,.0f} Cr"

ma50 = data["Close"].rolling(50).mean().iloc[-1]
ma200 = data["Close"].rolling(200).mean().iloc[-1]

returns = data["Close"].pct_change().dropna()
volatility = returns.std() * 100

# =========================================================
# 1️⃣ BUY / SELL DECISION (CORE)
# =========================================================
if section == "Buy / Sell Decision":
    st.subheader("📌 What should YOU do right now?")

    col1, col2, col3 = st.columns(3)

    col1.metric("Current Price", f"{currency}{price:.2f}", f"{change_pct:.2f}%")
    col2.metric("50-Day Avg", f"{currency}{ma50:.2f}")
    col3.metric("200-Day Avg", f"{currency}{ma200:.2f}")

    st.markdown("### 🔍 Decision Zones (Rule-Based)")

    if price > ma50 > ma200:
        st.success(
            f"""
**Trend:** Strong  
**Action:** Long-term investors may buy **only on dips near {currency}{ma50:.2f}**  
**Sell if:** Price closes below {currency}{ma200:.2f}  
"""
        )
    elif price < ma200:
        st.error(
            f"""
**Trend:** Weak  
**Action:** Avoid or exit  
**Reason:** Stock is below long-term support ({currency}{ma200:.2f})
"""
        )
    else:
        st.warning(
            f"""
**Trend:** Neutral  
**Action:** Wait  
**Reason:** Better risk-reward may appear near {currency}{ma50:.2f}
"""
        )

    st.markdown("""
**Important for beginners:**  
Never invest all money at one price.  
Good stocks also give bad entries.
""")

# =========================================================
# 2️⃣ FUNDAMENTALS DECODER (ALL KEY INDICATORS)
# =========================================================
elif section == "Fundamentals Decoder":
    st.subheader("📊 Fundamentals — Explained Clearly")

    fundamentals = {
        "Market Cap": cr(info.get("marketCap")),
        "P/E Ratio": info.get("trailingPE"),
        "P/B Ratio": info.get("priceToBook"),
        "ROE": info.get("returnOnEquity"),
        "ROCE": info.get("returnOnAssets"),
        "Debt": cr(info.get("totalDebt")),
        "Debt to Equity": info.get("debtToEquity"),
        "Revenue Growth": info.get("revenueGrowth"),
        "Profit Margin": info.get("profitMargins"),
        "Dividend Yield": info.get("dividendYield"),
    }

    df = pd.DataFrame(
        fundamentals.items(),
        columns=["Indicator", "Value"]
    )

    st.table(df)

    st.markdown("### 🧠 How to read this")

    if info.get("debtToEquity", 0) < 1:
        st.success("Debt is under control.")
    else:
        st.warning("Debt is high. Watch carefully.")

    if info.get("returnOnEquity", 0) and info.get("returnOnEquity") > 0.15:
        st.success("Business generates healthy returns on capital.")
    else:
        st.warning("Returns on capital are average or weak.")

# =========================================================
# 3️⃣ FINANCIAL HEALTH (BEGINNER-FRIENDLY)
# =========================================================
elif section == "Financial Health (Beginner)":
    st.subheader("🩺 Financial Health — Simple Language")

    cfo = info.get("operatingCashflow")
    profit_margin = info.get("profitMargins")

    st.markdown("### Cash Flow Check")

    if cfo and cfo > 0:
        st.success("Company generates real cash from operations.")
    else:
        st.error("Company struggles to generate cash.")

    st.markdown("### Profit Quality")

    if profit_margin and profit_margin > 0.15:
        st.success("Healthy profits. Business has pricing power.")
    else:
        st.warning("Thin profits. Business is under pressure.")

    st.markdown("### Beginner Verdict")

    if cfo and cfo > 0 and profit_margin and profit_margin > 0.15:
        st.success("Financially strong for long-term investors.")
    else:
        st.warning("Not financially ideal for beginners.")

# =========================================================
# 4️⃣ PORTFOLIO RISK CHECKER
# =========================================================
elif section == "Portfolio Risk Checker":
    st.subheader("⚠️ Portfolio Risk Reality Check")

    amount = st.number_input("Investment Amount (₹)", 50000)
    stocks = st.slider("Number of stocks in your portfolio", 1, 20, 5)
    risk = st.selectbox("Your Risk Appetite", ["Low", "Medium", "High"])

    st.markdown("### Risk Diagnosis")

    if stocks < 5:
        st.error("High concentration risk. One bad stock can hurt badly.")
    else:
        st.success("Diversification is reasonable.")

    if volatility > 2.5 and risk == "Low":
        st.error("Stock volatility does NOT match your risk appetite.")
    elif volatility < 1.5 and risk == "High":
        st.warning("You may be under-utilizing your risk capacity.")
    else:
        st.success("Risk profile is aligned.")

    st.markdown("""
**Truth:**  
Most losses come from poor risk control, not bad stocks.
""")

# ================== FOOTER ==================
st.markdown("---")
st.markdown(
    "<marquee>Investing is about managing risk, not predicting prices • Made by Kriya</marquee>",
    unsafe_allow_html=True
)
