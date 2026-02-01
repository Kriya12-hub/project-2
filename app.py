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
    st.error("No price data available.")
    st.stop()

price = price_data["Close"].iloc[-1]
currency = "₹" if symbol.endswith(".NS") else "$"

returns = price_data["Close"].pct_change().dropna()
volatility = returns.std() * 100
drawdown = (price_data["Close"] / price_data["Close"].cummax() - 1) * 100
max_dd = drawdown.min()

ma50 = price_data["Close"].rolling(50).mean()
ma200 = price_data["Close"].rolling(200).mean()

# =====================================================
# BUY / SELL DECISION + BUY/SELL ZONES
# =====================================================
if section == "Buy / Sell Decision":
    st.header("📌 Buy / Sell Decision")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{currency}{price:,.0f}")
    c2.metric("50 DMA", f"{currency}{ma50.iloc[-1]:,.0f}")
    c3.metric("200 DMA", f"{currency}{ma200.iloc[-1]:,.0f}")

    st.line_chart(price_data["Close"])

    if price > ma50.iloc[-1] > ma200.iloc[-1]:
        st.success("Trend: Strong Uptrend (Long-term positive)")
    elif price < ma200.iloc[-1]:
        st.error("Trend: Weak / Downtrend (Avoid fresh buying)")
    else:
        st.warning("Trend: Sideways (Wait for clarity)")

    # ---------- BUY / SELL ZONES ----------
    st.markdown("## 🎯 Buy & Sell Zones (Rule-Based)")

    recent = price_data["Close"].tail(120)
    support = recent.min()
    resistance = recent.max()

    buy_low, buy_high = support * 0.98, support * 1.02
    sell_low, sell_high = resistance * 0.98, resistance * 1.02

    st.line_chart(recent)

    z1, z2, z3 = st.columns(3)
    z1.metric("Buy Zone", f"{currency}{buy_low:,.0f} – {currency}{buy_high:,.0f}")
    z2.metric("Current Price", f"{currency}{price:,.0f}")
    z3.metric("Sell Zone", f"{currency}{sell_low:,.0f} – {currency}{sell_high:,.0f}")

    st.markdown(f"""
### 🧠 Interpretation
• Buy zone is derived from **historical demand (support)**  
• Sell zone comes from **historical supply (resistance)**  

**How to act**
1. Accumulate near **{currency}{buy_low:,.0f}–{currency}{buy_high:,.0f}**
2. Book partial profits near **{currency}{sell_low:,.0f}–{currency}{sell_high:,.0f}**
3. If price breaks below support → **trend weakens**
4. Best for **swing & positional investors**
""")

# =====================================================
# FUNDAMENTALS
# =====================================================
elif section == "Fundamentals Decoder":
    st.header("📘 Fundamentals Decoder")

    def metric(label, val):
        st.metric(label, val if val not in [None, ""] else "—")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric("Market Cap (Cr)", f"{info.get('marketCap',0)/1e7:.0f}")
        metric("P/E", info.get("trailingPE"))
        metric("Book Value", info.get("bookValue"))

    with c2:
        metric("Debt / Equity", info.get("debtToEquity"))
        metric("Profit Margin", info.get("profitMargins"))
        metric("ROE", info.get("returnOnEquity"))

    with c3:
        metric("52W High", info.get("fiftyTwoWeekHigh"))
        metric("52W Low", info.get("fiftyTwoWeekLow"))
        metric("Industry", info.get("industry"))

    st.markdown("""
### 🧠 What this means
• High debt = risk in downturns  
• High ROE = efficient capital usage  
• Very high P/E = growth already priced in  
""")

# =====================================================
# FINANCIAL HEALTH
# =====================================================
elif section == "Financial Health (Beginner)":
    st.header("💊 Financial Health (Beginner)")

    try:
        cf = stock.cashflow
    except:
        cf = pd.DataFrame()

    if cf.empty:
        st.warning("Cash-flow data unavailable.")
    else:
        cfo = cf.iloc[0].sum()
        if cfo > 0:
            st.success("Company generates positive operating cash.")
        else:
            st.error("Company struggles to generate cash.")

    st.markdown("""
• Cash flow keeps businesses alive  
• Profit without cash is dangerous  
• Debt + weak cash flow = red flag  
""")

# =====================================================
# BUSINESS PERFORMANCE
# =====================================================
elif section == "Business Performance":
    st.header("🏭 Business Performance (YoY)")

    try:
        fin = stock.financials
    except:
        fin = pd.DataFrame()

    if fin.empty:
        st.warning("Financial statement data unavailable.")
        st.stop()

    revenue = fin.loc["Total Revenue"].head(2)
    profit = fin.loc["Net Income"].head(2)

    df = pd.DataFrame(
        {"Revenue": revenue.values, "Net Profit": profit.values},
        index=["Previous Year", "Latest Year"]
    )

    st.bar_chart(df)

    st.markdown("""
### 🧠 Interpretation
• Revenue ↑ = demand & scale  
• Profit ↑ = efficiency & pricing power  
• Revenue ↑ but profit ↓ = cost pressure  
""")

# =====================================================
# PORTFOLIO SIMULATION
# =====================================================
elif section == "Portfolio Simulation":
    st.header("📈 Portfolio Simulation")

    amount = st.number_input("Investment Amount (₹)", 10000, value=100000, step=10000)
    years = st.slider("Years", 1, 10, 3)

    data = price_data.tail(years * 252)
    units = amount / data["Close"].iloc[0]
    portfolio = units * data["Close"]

    cagr = ((portfolio.iloc[-1] / amount) ** (1/years) - 1) * 100
    dd = (portfolio / portfolio.cummax() - 1).min() * 100

    st.line_chart(portfolio)

    c1, c2, c3 = st.columns(3)
    c1.metric("Final Value", f"₹{portfolio.iloc[-1]:,.0f}")
    c2.metric("CAGR", f"{cagr:.2f}%")
    c3.metric("Max Drawdown", f"{dd:.2f}%")

# =====================================================
# PORTFOLIO ALLOCATION (BUG-SAFE)
# =====================================================
elif section == "Portfolio Allocation":
    st.header("🧩 Portfolio Allocation")

    syms = st.text_input(
        "Enter symbols (comma separated)",
        "RELIANCE.NS, TCS.NS, HDFCBANK.NS"
    )
    tickers = [s.strip() for s in syms.split(",")]

    raw = yf.download(tickers, period="5y", group_by="ticker")
    prices = {}

    for t in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                prices[t] = raw[t]["Close"]
            else:
                prices[t] = raw["Close"]
        except:
            pass

    data = pd.DataFrame(prices).dropna()
    if data.empty:
        st.error("Portfolio data unavailable.")
        st.stop()

    rets = data.pct_change().dropna()
    weights = np.array([1/len(tickers)] * len(tickers))
    port = (1 + rets.dot(weights)).cumprod()

    st.line_chart(port)

# =====================================================
# MONTE CARLO SIMULATION + EXPLANATION
# =====================================================
elif section == "Monte Carlo Simulation":
    st.header("🔮 Monte Carlo Simulation")

    log_ret = np.log(price_data["Close"] / price_data["Close"].shift(1)).dropna()
    mu, sigma = log_ret.mean(), log_ret.std()

    years = st.slider("Years into future", 1, 10, 3)
    days = years * 252
    sims = 500

    paths = np.zeros((days, sims))
    paths[0] = price

    for t in range(1, days):
        paths[t] = paths[t-1] * np.exp(mu + sigma * np.random.randn(sims))

    st.line_chart(paths[:, :50])

    final = paths[-1]
    p10, p50, p90 = np.percentile(final, [10, 50, 90])

    c1, c2, c3 = st.columns(3)
    c1.metric("Worst Case (10%)", f"{currency}{p10:,.0f}")
    c2.metric("Most Likely", f"{currency}{p50:,.0f}")
    c3.metric("Best Case (90%)", f"{currency}{p90:,.0f}")

    st.markdown(f"""
### 🧠 How to read this
• Lines = possible futures, not predictions  
• Focus on **zones**, not individual paths  

**Decision guide**
1. Can you tolerate fall to **{currency}{p10:,.0f}**?
2. If yes → long-term holding possible  
3. If no → reduce position size  
""")

# =====================================================
# NEWS & SENTIMENT
# =====================================================
elif section == "News & Sentiment":
    st.header("📰 News & Sentiment Impact")

    try:
        news = stock.news
    except:
        news = []

    if not news:
        st.warning("No recent news found.")
    else:
        for n in news[:5]:
            title = n.get("title", "News")
            link = n.get("link", "#")
            st.markdown(f"### 🔗 [{title}]({link})")

            text = title.lower()
            if any(w in text for w in ["growth", "profit", "expansion", "deal"]):
                st.success("Impact: Positive")
            elif any(w in text for w in ["loss", "decline", "debt", "lawsuit"]):
                st.error("Impact: Negative")
            else:
                st.info("Impact: Neutral")

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("ALPHA STACK • Decision Intelligence System • Built by Kriya")
