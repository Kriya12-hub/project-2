import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ================== PAGE CONFIG ==================
st.set_page_config(page_title="ALPHA STACK", layout="wide")

# ================== HEADER ==================
st.markdown("""
<style>
.header {
    display:flex;
    justify-content:space-between;
    align-items:center;
}
.logo {
    font-size:32px;
    font-weight:800;
}
.subtitle {
    font-size:14px;
    color:gray;
}
.section {
    margin-top:30px;
}
</style>

<div class="header">
    <div>
        <div class="logo">🟢 ALPHA STACK</div>
        <div class="subtitle">Market Intelligence • Not Predictions</div>
    </div>
</div>

<marquee>
Built for disciplined investors • Data over emotion • Made by Kriya
</marquee>
""", unsafe_allow_html=True)

st.markdown("---")

# ================== SIDEBAR ==================
st.sidebar.title("Navigation")

section = st.sidebar.radio(
    "",
    [
        "Market Overview",
        "Deep Analysis",
        "Fundamentals Decoder",
        "Financial Health (Beginner)",
        "Buy / Sell Decision",
        "News & Sentiment Analysis"
    ]
)

st.sidebar.caption("Built for clarity, not hype")

# ================== INPUT ==================
symbol = st.text_input("Enter Stock Symbol (.NS for India)", "RELIANCE.NS")

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

ma50 = price_data["Close"].rolling(50).mean()
ma200 = price_data["Close"].rolling(200).mean()

cum_max = price_data["Close"].cummax()
drawdown = (price_data["Close"] - cum_max) / cum_max * 100
max_dd = drawdown.min()

years = len(price_data) / 252
cagr = (price_data["Close"].iloc[-1] / price_data["Close"].iloc[0]) ** (1/years) - 1

# ================== ROE & ROCE (DERIVED) ==================
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

    c1, c2, c3 = st.columns(3)
    c1.metric("Current Price", f"{currency}{price:.2f}")
    c2.metric("Annualized Return (3Y)", f"{cagr*100:.2f}%")
    c3.metric("Volatility", f"{volatility:.2f}%")

    st.line_chart(price_data["Close"])

    st.markdown("""
**Conclusion**
- CAGR shows long-term wealth creation ability.
- Volatility indicates emotional difficulty.
- Price trend reflects market confidence.
""")

# ================== DEEP ANALYSIS ==================
elif section == "Deep Analysis":
    st.subheader("🔍 Deep Analysis — Price, Risk & Business Reality")

    # BUY / SELL ZONES
    st.markdown("### 📈 Buy & Sell Zones (Rule-Based)")

    support = price_data["Close"].rolling(20).min().iloc[-1]
    resistance = price_data["Close"].rolling(20).max().iloc[-1]

    df = price_data[["Close"]].copy()
    df["Support (Buy Zone)"] = support
    df["Resistance (Sell Zone)"] = resistance

    st.line_chart(df)

    st.markdown("""
**Inference**
- Buy near support improves risk–reward.
- Avoid fresh buying near resistance.
- Stops are mandatory below support.
""")

    # VOLATILITY
    st.markdown("### ⚠️ Volatility & Risk")

    risk_level = "Low" if volatility < 1.5 else "Medium" if volatility < 2.5 else "High"
    st.metric("Volatility Level", f"{volatility:.2f}%", risk_level)

    st.markdown("""
**Inference**
- High volatility = higher emotional pressure.
- Suitable investors depend on this number.
""")

    # DRAWDOWN
    st.markdown("### 📉 Worst Historical Loss")

    st.line_chart(drawdown)

    st.markdown(f"""
**Inference**
- Maximum drawdown: **{max_dd:.2f}%**
- This is the worst pain investors faced.
- Ask yourself: *Can I hold during this?*
""")

    # FINANCIAL PERFORMANCE
    st.markdown("### 💰 Business Performance (YoY)")

    if not financials.empty:
        try:
            perf = pd.DataFrame({
                "Revenue": financials.loc["Total Revenue"].iloc[:2],
                "Net Profit": financials.loc["Net Income"].iloc[:2]
            }).T
            st.bar_chart(perf)

            st.markdown("""
**Inference**
- Revenue growth = business expansion.
- Profit growth > revenue = efficiency.
""")
        except:
            st.warning("Detailed financial data unavailable.")

    # CASH FLOW
    st.markdown("### 💵 Cash Flow Quality")

    cfo = None
    for key in ["Total Cash From Operating Activities", "Operating Cash Flow"]:
        if not cashflow.empty and key in cashflow.index:
            cfo = cashflow.loc[key]
            break

    if cfo is not None:
        st.line_chart(cfo)
        st.markdown("""
**Inference**
- Consistent positive cash flow confirms earnings quality.
- Profit without cash is a red flag.
""")
    else:
        st.warning("Cash flow data not consistently available.")

    # FINAL SUMMARY
    st.markdown("## 🧠 FINAL ANALYST VERDICT")

    st.markdown("""
**Long-Term Investors**
- Enter near support with patience.
- Ignore short-term noise.
- Suitable if you can tolerate drawdowns.

**Short-Term Traders**
- Buy only near support.
- Exit near resistance.
- Strict stop-loss required.

**Intraday Traders**
- Not ideal unless volatility expands.

**Bottom Line**
This stock rewards **discipline and patience**, not predictions.
""")

# ================== FUNDAMENTALS ==================
elif section == "Fundamentals Decoder":
    st.subheader("📘 Fundamentals Decoder")

    df = pd.DataFrame({
        "Metric": ["ROE", "ROCE", "Debt to Equity", "Profit Margin", "Dividend Yield"],
        "Value": [
            f"{roe*100:.2f}%" if roe else "Data unavailable",
            f"{roce*100:.2f}%" if roce else "Data unavailable",
            info.get("debtToEquity"),
            info.get("profitMargins"),
            info.get("dividendYield")
        ]
    })

    st.table(df)

    st.markdown("""
**Conclusion**
- ROE & ROCE show capital efficiency.
- Debt levels define risk.
- Margins show business strength.
""")

# ================== FINANCIAL HEALTH ==================
elif section == "Financial Health (Beginner)":
    st.subheader("🩺 Financial Health — Simple Language")

    if roe and roe > 0.15 and cfo is not None:
        st.success("Financially strong business.")
    else:
        st.warning("Financial strength is average or inconsistent.")

    st.markdown("""
**Beginner Takeaway**
- Strong companies generate cash.
- Debt must be manageable.
- Ignore hype, follow numbers.
""")

# ================== BUY / SELL ==================
elif section == "Buy / Sell Decision":
    st.subheader("🎯 Buy / Sell Decision")

    if price > ma50.iloc[-1] > ma200.iloc[-1]:
        st.success("Trend is strong. Buy on dips near support.")
    elif price < ma200.iloc[-1]:
        st.error("Trend is weak. Avoid or exit.")
    else:
        st.warning("Trend is sideways. Wait for clarity.")

# ================== NEWS ==================
elif section == "News & Sentiment Analysis":
    st.subheader("📰 News & Sentiment Impact")

    news = stock.news[:10]

    if not news:
        st.info("No major recent news.")
    else:
        for n in news:
            title = n.get("title", "")
            link = n.get("link") or n.get("url")
            source = n.get("publisher", "Unknown")

            if link:
                st.markdown(f"**[{title}]({link})**")
            else:
                st.markdown(f"**{title}**")

            st.caption(f"Source: {source}")

            t = title.lower()
            if any(w in t for w in ["profit", "growth", "order", "expansion"]):
                st.success("Positive Impact")
            elif any(w in t for w in ["loss", "risk", "decline"]):
                st.error("Negative Impact")
            else:
                st.info("Neutral Impact")

            st.markdown("---")

# ================== FOOTER ==================
st.markdown("---")
st.caption("ALPHA STACK • Decision Intelligence System • Built by Kriya")
