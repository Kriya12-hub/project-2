import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="ALPHA STACK", layout="wide")

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<h1>🟢 ALPHA STACK</h1>
<p style="color:gray;">Market Intelligence • Built for decisions, not predictions</p>
<marquee>Risk management > return chasing • Made by Kriya</marquee>
<hr>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "",
    [
        "Buy / Sell Decision",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Business Performance",
        "Portfolio Simulation",
        "Portfolio Allocation",
        "Monte Carlo Simulation",
        "News & Sentiment",
    ]
)

symbol = st.sidebar.text_input("Stock Symbol (.NS for India)", "RELIANCE.NS")

# =====================================================
# DATA LOADING (SAFE)
# =====================================================
@st.cache_data
def load_data(symbol):
    t = yf.Ticker(symbol)
    hist = t.history(period="5y")
    info = t.info
    return hist, info  
    
price_data, info = load_data(symbol)
stock = yf.Ticker(symbol)


if price_data.empty:
    st.error("No data available.")
    st.stop()

price = price_data["Close"].iloc[-1]
currency = "₹" if symbol.endswith(".NS") else "$"

returns = price_data["Close"].pct_change().dropna()
volatility = returns.std() * 100

ma50 = price_data["Close"].rolling(50).mean()
ma200 = price_data["Close"].rolling(200).mean()

# =====================================================
# BUY / SELL DECISION
# =====================================================
if section == "Buy / Sell Decision":
    st.header("📌 Buy / Sell Decision")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{currency}{price:,.0f}")
    c2.metric("50 DMA", f"{currency}{ma50.iloc[-1]:,.0f}")
    c3.metric("200 DMA", f"{currency}{ma200.iloc[-1]:,.0f}")

    st.line_chart(price_data["Close"])

    recent = price_data["Close"].tail(120)
    support = recent.min()
    resistance = recent.max()

    st.markdown(f"""
### 🎯 Buy / Sell Zones
• **Buy near:** {currency}{support:,.0f}  
• **Sell near:** {currency}{resistance:,.0f}

**Interpretation**
1. Buying near support reduces downside risk  
2. Selling near resistance avoids greed traps  
3. Best suited for swing & positional investors  
""")

# =====================================================
# FUNDAMENTALS
# =====================================================
elif section == "Fundamentals Decoder":
    st.header("📘 Fundamentals Decoder")

    c1, c2, c3 = st.columns(3)
    c1.metric("Market Cap (Cr)", f"{info.get('marketCap',0)/1e7:.0f}")
    c1.metric("P/E", info.get("trailingPE"))
    c2.metric("Debt / Equity", info.get("debtToEquity"))
    c2.metric("ROE", info.get("returnOnEquity"))
    c3.metric("52W High", info.get("fiftyTwoWeekHigh"))
    c3.metric("52W Low", info.get("fiftyTwoWeekLow"))

    st.markdown("""
### 🧠 How to read this
• High ROE = efficient business  
• High debt = risky in downturns  
• Very high P/E = expectations already priced in  
""")

# =====================================================
# FINANCIAL HEALTH
# =====================================================
elif section == "Financial Health (Beginner)":
    st.header("💊 Financial Health")

    cf = stock.cashflow
    if cf.empty:
        st.warning("Cash flow data unavailable.")
    else:
        cfo = cf.iloc[0].sum()
        st.success("Positive operating cash flow") if cfo > 0 else st.error("Weak cash flow")

    st.markdown("""
• Cash flow is oxygen for companies  
• Profits without cash = danger  
• Debt + weak cash = red flag  
""")

# =====================================================
# BUSINESS PERFORMANCE (MATCHES YOUR SKETCH)
# =====================================================
elif section == "Business Performance":
    st.header("🏭 Business Performance (YoY)")

    fin = stock.financials
    if fin.empty:
        st.warning("Data unavailable.")
        st.stop()

    data = pd.DataFrame({
        "Revenue": fin.loc["Total Revenue"].head(2).values,
        "Net Profit": fin.loc["Net Income"].head(2).values
    }, index=["Previous Year", "Latest Year"])

    st.bar_chart(data)

    st.markdown("""
### 🧠 Interpretation
1. Revenue growth shows demand strength  
2. Profit growth shows cost control  
3. Revenue ↑ but profit ↓ = margin pressure  
4. Healthy companies grow both together  
""")

# =====================================================
# PORTFOLIO SIMULATION
# =====================================================
elif section == "Portfolio Simulation":
    st.header("📈 Portfolio Simulation")

    amount = st.number_input("Investment Amount (₹)", 10000, value=100000)
    years = st.slider("Years", 1, 10, 3)

    data = price_data.tail(years * 252)
    units = amount / data["Close"].iloc[0]
    portfolio = units * data["Close"]

    st.line_chart(portfolio)

    st.markdown("""
### 🧠 What this tells you
• Shows wealth growth over time  
• Highlights drawdowns emotionally investors panic at  
• Helps decide position sizing  
""")

# =====================================================
# PORTFOLIO ALLOCATION
# =====================================================
elif section == "Portfolio Allocation":
    st.header("🧩 Portfolio Allocation")

    syms = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    data = yf.download(syms, period="5y")["Close"]

    rets = data.pct_change().dropna()
    weights = np.array([1/len(syms)] * len(syms))
    port = (1 + rets.dot(weights)).cumprod()

    st.line_chart(port)

    st.markdown("""
### 🧠 Interpretation
1. Diversification smooths volatility  
2. No single stock controls outcome  
3. Reduces emotional decision-making  
""")

# =====================================================
# MONTE CARLO (SIMPLIFIED & UNDERSTANDABLE)
# =====================================================
elif section == "Monte Carlo Simulation":
    st.header("🔮 Monte Carlo Simulation")

    log_ret = np.log(price_data["Close"] / price_data["Close"].shift(1)).dropna()
    mu, sigma = log_ret.mean(), log_ret.std()

    paths = []
    for _ in range(10):  # MAX 10 lines only
        prices = [price]
        for _ in range(252 * 3):
            prices.append(prices[-1] * np.exp(mu + sigma * np.random.randn()))
        paths.append(prices)

    st.line_chart(pd.DataFrame(paths).T)

    st.markdown("""
### 🧠 How to understand this
• Each line = one possible future  
• Wider spread = higher risk  
• Focus on downside comfort, not upside fantasy  

**Investor takeaway**
If worst paths scare you → position too big  
""")

# =====================================================
# NEWS & SENTIMENT
# =====================================================
elif section == "News & Sentiment":
    st.header("📰 News & Sentiment")

    news = stock.news
    if not news:
        st.warning("No recent news.")
    else:
        for n in news[:5]:
            title = n.get("title", "")
            link = n.get("link", "")
            st.markdown(f"### 🔗 [{title}]({link})")

            t = title.lower()
            if any(w in t for w in ["profit", "growth", "expansion"]):
                st.success("Impact: Positive")
            elif any(w in t for w in ["loss", "decline", "debt"]):
                st.error("Impact: Negative")
            else:
                st.info("Impact: Neutral")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("ALPHA STACK • Decision Intelligence System • Built by Kriya")
