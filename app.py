import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="ALPHA STACK", layout="wide")

# -----------------------------
# DATA LOADER (SAFE)
# -----------------------------
@st.cache_data
def load_price(symbol):
    df = yf.download(symbol, period="5y", progress=False)
    return df

def get_ticker(symbol):
    return yf.Ticker(symbol)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("ALPHA STACK")
page = st.sidebar.radio(
    "Navigation",
    [
        "Buy / Sell Decision",
        "Deep Analysis",
        "Business Performance",
        "Portfolio Allocation",
        "Monte Carlo Simulation",
        "News & Sentiment"
    ]
)

symbol = st.sidebar.text_input("Stock Symbol (.NS for India)", "RELIANCE.NS")

price = load_price(symbol)
ticker = get_ticker(symbol)

# -----------------------------
# BUY / SELL DECISION
# -----------------------------
if page == "Buy / Sell Decision":
    st.header("📌 Buy / Sell Decision")

    close = price["Close"]
    current_price = close.iloc[-1]

    support = close.rolling(200).min().iloc[-1]
    resistance = close.rolling(200).max().iloc[-1]

    st.metric("Current Price", f"₹{current_price:,.2f}")
    st.metric("Strong Buy Zone", f"₹{support:,.0f}")
    st.metric("Sell / Profit Zone", f"₹{resistance:,.0f}")

    st.markdown("""
### Interpretation
• If price is **near support**, risk is low → **Accumulation zone**  
• If price is **near resistance**, upside is limited → **Book profits**  
• If price is mid-range → **Wait, don’t chase**
""")

# -----------------------------
# DEEP ANALYSIS
# -----------------------------
elif page == "Deep Analysis":
    st.header("📊 Deep Analysis")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price.index, y=price["Close"], name="Price"))
    fig.add_hline(y=price["Close"].rolling(200).mean().iloc[-1], line_dash="dash", name="200 DMA")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
### What this chart tells you
• Trend direction using **200-DMA**  
• Buying near DMA reduces downside risk  
• Strong trends stay above DMA  
• Below DMA = caution zone  
• Best for **positional & long-term investors**
""")

# -----------------------------
# BUSINESS PERFORMANCE
# -----------------------------
elif page == "Business Performance":
    st.header("🏭 Business Performance (YoY)")

    try:
        fin = ticker.financials
        rev = fin.loc["Total Revenue"]
        prof = fin.loc["Net Income"]

        df = pd.DataFrame({
            "Revenue": rev,
            "Net Profit": prof
        }).dropna().T

        fig = go.Figure()
        for col in df.columns:
            fig.add_bar(name=col, x=df.index, y=df[col])

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
### Interpretation
• Revenue growth = business demand  
• Profit growth = pricing power  
• Profit < Revenue growth = margin pressure  
• Consistent bars = stable company  
• Volatile profits = cyclical risk
""")
    except:
        st.warning("Business financials not fully available.")

# -----------------------------
# PORTFOLIO ALLOCATION
# -----------------------------
elif page == "Portfolio Allocation":
    st.header("📦 Portfolio Allocation")

    weights = {
        "Large Cap": 50,
        "Mid Cap": 30,
        "Cash": 20
    }

    fig = go.Figure(data=[go.Pie(labels=list(weights.keys()), values=list(weights.values()))])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
### Allocation Logic
• Large cap = stability  
• Mid cap = growth engine  
• Cash = downside protection  
• Reduces emotional decision-making  
• Ideal for **beginners & professionals**
""")

# -----------------------------
# MONTE CARLO (SIMPLIFIED)
# -----------------------------
elif page == "Monte Carlo Simulation":
    st.header("🔮 Monte Carlo Simulation (Simplified)")

    returns = price["Close"].pct_change().dropna()
    mu, sigma = returns.mean(), returns.std()
    last_price = price["Close"].iloc[-1]

    simulations = []
    for i in range(10):  # ONLY 10 LINES
        prices = [last_price]
        for _ in range(252 * 3):
            prices.append(prices[-1] * np.exp(np.random.normal(mu, sigma)))
        simulations.append(prices)

    fig = go.Figure()
    for i, sim in enumerate(simulations):
        fig.add_trace(go.Scatter(y=sim, mode="lines", name=f"Path {i+1}"))

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
### How to read this
• Each line = one possible future  
• Upper paths = optimistic outcome  
• Lower paths = worst-case risk  
• Middle cluster = most likely range  
• Helps decide **risk tolerance**
""")

    st.markdown("""
### Final Insight
• Long-term investors focus on **median path**  
• Traders focus on **downside risk**  
• If worst-case scares you → reduce position size
""")

# -----------------------------
# NEWS & SENTIMENT
# -----------------------------
elif page == "News & Sentiment":
    st.header("📰 News & Sentiment Impact")

    news = ticker.news[:5]

    for n in news:
        title = n.get("title", "News")
        link = n.get("link", "")
        sentiment = "Neutral"

        if "profit" in title.lower() or "growth" in title.lower():
            sentiment = "Positive"
        elif "loss" in title.lower() or "debt" in title.lower():
            sentiment = "Negative"

        st.markdown(f"### [{title}]({link})")
        st.markdown(f"**Impact:** {sentiment}")
        st.divider()

    st.markdown("""
### How to use news
• Positive news = short-term momentum  
• Negative news = volatility spike  
• Neutral news = ignore noise  
• Price reaction matters more than headline
""")

# -----------------------------
# FOOTER
# -----------------------------
st.divider()
st.markdown("**ALPHA STACK** — Data → Conviction | Made by Kriya")
