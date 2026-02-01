import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ================= PAGE CONFIG =================
st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ================= HEADER =================
st.markdown("""
<h1>🟢 ALPHA STACK</h1>
<p style="color:gray;">Market Intelligence • Built for decisions, not predictions</p>
<marquee>Risk management > return chasing • Made by Kriya</marquee>
<hr>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.title("Navigation")
section = st.sidebar.radio(
    "",
    [
        "Buy / Sell Decision",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Portfolio Simulation",
        "Portfolio Allocation",
        "Monte Carlo Simulation",
    ]
)

symbol = st.sidebar.text_input("Stock Symbol (.NS for India)", "RELIANCE.NS")

# ================= DATA LOADING (SAFE) =================
@st.cache_data
def load_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="5y")
    info = ticker.info
    return hist, info

price_data, info = load_data(symbol)
stock = yf.Ticker(symbol)  # NOT cached (important)

if price_data.empty:
    st.error("No data available for this symbol.")
    st.stop()

price = price_data["Close"].iloc[-1]
currency = "₹" if symbol.endswith(".NS") else "$"

# ================= COMMON METRICS =================
returns = price_data["Close"].pct_change().dropna()
volatility = returns.std() * 100

ma50 = price_data["Close"].rolling(50).mean()
ma200 = price_data["Close"].rolling(200).mean()

drawdown = (price_data["Close"] / price_data["Close"].cummax() - 1) * 100
max_dd = drawdown.min()

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

    if price > ma50.iloc[-1] > ma200.iloc[-1]:
        st.success("""
**Trend: Strong Uptrend**

• Long-term investors: Buy on dips  
• Short-term traders: Buy near 50 DMA  
• Exit if price breaks below 200 DMA  
""")
    elif price < ma200.iloc[-1]:
        st.error("""
**Trend: Weak**

• Avoid fresh buying  
• Existing investors should protect capital  
""")
    else:
        st.warning("""
**Trend: Sideways**

• Wait for clarity  
• Risk–reward not attractive right now  
""")

# =====================================================
# FUNDAMENTALS
# =====================================================
elif section == "Fundamentals Decoder":
    st.header("📘 Fundamentals Decoder")

    def show(label, value):
        st.metric(label, value if value else "—")

    c1, c2, c3 = st.columns(3)

    with c1:
        show("Market Cap (Cr)", f"{info.get('marketCap',0)/1e7:.0f}")
        show("P/E Ratio", info.get("trailingPE"))
        show("Book Value", info.get("bookValue"))

    with c2:
        show("Debt to Equity", info.get("debtToEquity"))
        show("Profit Margin", info.get("profitMargins"))
        show("Dividend Yield", info.get("dividendYield"))

    with c3:
        show("52W High", info.get("fiftyTwoWeekHigh"))
        show("52W Low", info.get("fiftyTwoWeekLow"))
        show("Industry", info.get("industry"))

    st.markdown("""
### Interpretation
• Lower debt = safer during downturns  
• High margins = pricing power  
• Very high P/E = future growth already priced in  
""")

# =====================================================
# FINANCIAL HEALTH (BEGINNER)
# =====================================================
elif section == "Financial Health (Beginner)":
    st.header("💊 Financial Health (Simple Language)")

    try:
        cashflow = stock.cashflow
    except:
        cashflow = pd.DataFrame()

    if cashflow.empty:
        st.warning("Cash flow data not available.")
    else:
        cfo = cashflow.iloc[0].sum()
        if cfo > 0:
            st.success("✅ Company generates positive operating cash.")
        else:
            st.error("❌ Company struggles to generate cash.")

    st.markdown("""
### Beginner Verdict
• Cash generation keeps companies alive  
• Profit without cash is risky  
• Debt + weak cash flow = danger  
""")

# =====================================================
# PORTFOLIO SIMULATION (SINGLE STOCK)
# =====================================================
elif section == "Portfolio Simulation":
    st.header("📈 Portfolio Simulation")

    amount = st.number_input("Investment Amount (₹)", 10000, value=100000, step=10000)
    years = st.slider("Investment Duration (Years)", 1, 10, 3)

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

    st.markdown("""
**Interpretation**
• Can you tolerate this drawdown emotionally?  
• Returns are useless if risk is unbearable  
""")

# =====================================================
# MULTI-STOCK PORTFOLIO ALLOCATION
# =====================================================
elif section == "Portfolio Allocation":
    st.header("🧩 Portfolio Allocation")

    symbols = st.text_input(
        "Enter symbols (comma separated)",
        "RELIANCE.NS, TCS.NS, HDFCBANK.NS"
    )

    tickers = [s.strip() for s in symbols.split(",")]
    data = yf.download(tickers, period="5y")["Adj Close"]

    if data.isnull().all().any():
        st.error("One or more symbols have insufficient data.")
        st.stop()

    returns = data.pct_change().dropna()
    weights = np.array([1/len(tickers)] * len(tickers))
    portfolio_returns = returns.dot(weights)
    cumulative = (1 + portfolio_returns).cumprod()

    vol = portfolio_returns.std() * 100
    dd = (cumulative / cumulative.cummax() - 1).min() * 100

    st.line_chart(cumulative)

    c1, c2, c3 = st.columns(3)
    c1.metric("Volatility", f"{vol:.2f}%")
    c2.metric("Max Drawdown", f"{dd:.2f}%")
    c3.metric("Stocks", len(tickers))

    st.markdown("""
**Interpretation**
• Diversification smooths returns  
• Portfolio risk < individual stock risk  
""")

# =====================================================
# MONTE CARLO SIMULATION
# =====================================================
elif section == "Monte Carlo Simulation":
    st.header("🔮 Monte Carlo Simulation")

    returns = np.log(price_data["Close"] / price_data["Close"].shift(1)).dropna()
    mu, sigma = returns.mean(), returns.std()

    years = st.slider("Years into future", 1, 10, 3)
    days = years * 252
    sims = 500

    paths = np.zeros((days, sims))
    paths[0] = price

    for t in range(1, days):
        paths[t] = paths[t-1] * np.exp(mu + sigma * np.random.randn(sims))

    st.line_chart(paths[:, :50])

    final_prices = paths[-1]
    p10, p50, p90 = np.percentile(final_prices, [10, 50, 90])

    c1, c2, c3 = st.columns(3)
    c1.metric("Worst Case (10%)", f"₹{p10:,.0f}")
    c2.metric("Most Likely", f"₹{p50:,.0f}")
    c3.metric("Best Case (90%)", f"₹{p90:,.0f}")

    st.markdown("""
**Interpretation**
• This is probability, not prediction  
• If worst case scares you → reduce position size  
• Long-term edge exists only if downside is survivable  
""")

# ================= FOOTER =================
st.markdown("---")
st.caption("ALPHA STACK • Decision Intelligence System • Built by Kriya")
