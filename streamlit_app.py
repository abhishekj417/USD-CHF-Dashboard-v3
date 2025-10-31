import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(page_title="USD/CHF Dashboard", layout="wide")

st.title("💵 USD/CHF 30-Year Macro Dashboard")

@st.cache_data(ttl=86400)
def get_data():
   start_date = "1995-01-01"
   end_date = datetime.today().strftime("%Y-%m-%d")

   # Main USD/CHF pair
   usdchf = yf.download("USDCHF=X", start=start_date, end=end_date, interval="1mo")["Adj Close"]

   # Comparison assets
   gold = yf.download("GC=F", start=start_date, end=end_date, interval="1mo")["Adj Close"]
   oil = yf.download("CL=F", start=start_date, end=end_date, interval="1mo")["Adj Close"]
   sp500 = yf.download("^GSPC", start=start_date, end=end_date, interval="1mo")["Adj Close"]
   cpi_proxy = yf.download("^IRX", start=start_date, end=end_date, interval="1mo")["Adj Close"]  # 3-Month T-Bill Rate proxy for CPI
   gdp_proxy = yf.download("^IXIC", start=start_date, end=end_date, interval="1mo")["Adj Close"]  # Nasdaq proxy for economic cycle

   # Combine all
   df = pd.DataFrame({
       "USDCHF": usdchf,
       "Gold": gold,
       "Oil": oil,
       "S&P500": sp500,
       "CPI_Proxy": cpi_proxy,
       "GDP_Proxy": gdp_proxy
   })

   df = df.dropna()
   return df

data = get_data()

# Sidebar selection
st.sidebar.header("Select Comparison Variable")
variable = st.sidebar.selectbox(
   "Compare USD/CHF against:",
   ["Gold", "Oil", "S&P500", "CPI_Proxy", "GDP_Proxy"]
)

# Chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["USDCHF"], name="USD/CHF", line=dict(color="blue", width=2)))
fig.add_trace(go.Scatter(x=data.index, y=data[variable], name=variable, line=dict(color="orange", width=2, dash="dot"), yaxis="y2"))

fig.update_layout(
   title=f"USD/CHF vs {variable} (1995–Present)",
   xaxis_title="Date",
   yaxis_title="USD/CHF Rate",
   yaxis2=dict(title=variable, overlaying="y", side="right"),
   hovermode="x unified",
   template="plotly_dark",
   legend=dict(x=0.02, y=0.98)
)

st.plotly_chart(fig, use_container_width=True)

# Data table
st.subheader("📊 Monthly Historical Data (Last 36 months)")
st.dataframe(data.tail(36))

st.caption("Data updates daily from Yahoo Finance. No API keys needed.")
