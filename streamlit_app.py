import streamlit as st
import pandas as pd
import yfinance as yf
from fredapi import Fred
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="USD/CHF Macro Dashboard", layout="wide")

st.title("💵 USD/CHF Exchange Rate - 30-Year Macro Dashboard")

# Load FRED API key
fred = Fred(api_key=st.secrets["FRED_API_KEY"])

# ---------------------------
# FETCH DATA
# ---------------------------

@st.cache_data(ttl=86400)  # Cache for 1 day
def get_data():
   start_date = "1995-01-01"
   end_date = datetime.today().strftime("%Y-%m-%d")

   # 1️⃣ USD/CHF Exchange Rate (from Yahoo Finance)
   usdchf = yf.download("USDCHF=X", start=start_date, end=end_date, interval="1mo")["Adj Close"]

   # 2️⃣ Gold, Oil, and S&P500
   gold = yf.download("GC=F", start=start_date, end=end_date, interval="1mo")["Adj Close"]
   oil = yf.download("CL=F", start=start_date, end=end_date, interval="1mo")["Adj Close"]
   sp500 = yf.download("^GSPC", start=start_date, end=end_date, interval="1mo")["Adj Close"]

   # 3️⃣ FRED Macro Variables
   cpi = fred.get_series("CPIAUCSL")  # Consumer Price Index
   fed_rate = fred.get_series("FEDFUNDS")  # Fed Funds Rate
   gdp = fred.get_series("GDP")  # GDP (Quarterly, interpolated)
   exports = fred.get_series("BOPGSTB")  # Exports of goods & services

   # Convert to monthly data & merge
   df = pd.DataFrame({
       "USDCHF": usdchf,
       "Gold": gold,
       "Oil": oil,
       "S&P500": sp500
   })

   df.index = pd.to_datetime(df.index)
   df = df.resample("M").last()

   macro = pd.DataFrame({
       "CPI": cpi,
       "FedFunds": fed_rate,
       "GDP": gdp,
       "Exports": exports
   })
   macro.index = pd.to_datetime(macro.index)
   macro = macro.resample("M").ffill()

   merged = df.join(macro, how="inner")
   return merged

data = get_data()

# ---------------------------
# DASHBOARD UI
# ---------------------------

st.sidebar.header("Select Variable to Compare")
variable = st.sidebar.selectbox(
   "Choose a variable to analyze against USD/CHF:",
   ["Gold", "Oil", "S&P500", "CPI", "FedFunds", "GDP", "Exports"]
)

st.sidebar.markdown("---")
st.sidebar.write("Data from: Yahoo Finance & FRED (Federal Reserve Economic Data)")

# ---------------------------
# CHARTS
# ---------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(
   x=data.index, y=data["USDCHF"],
   name="USD/CHF", line=dict(color="blue", width=2)
))
fig.add_trace(go.Scatter(
   x=data.index, y=data[variable],
   name=variable, line=dict(color="orange", width=2, dash="dot"),
   yaxis="y2"
))

fig.update_layout(
   title=f"USD/CHF vs {variable} (1995–Present)",
   xaxis_title="Date",
   yaxis_title="USD/CHF Exchange Rate",
   yaxis2=dict(title=variable, overlaying="y", side="right"),
   hovermode="x unified",
   template="plotly_dark",
   legend=dict(x=0.02, y=0.98)
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# DATA TABLE
# ---------------------------
st.subheader("📊 Monthly Historical Data (Last 30 Years)")
st.dataframe(data.tail(36))  # Show last 3 years

st.caption("Data automatically updates daily from Yahoo Finance and FRED.")
