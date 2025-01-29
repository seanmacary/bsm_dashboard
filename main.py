import streamlit as st
from utils import (
    scrape_spy_tickers, get_cur_risk_free_rate, calc_historical_volatility
)
import yfinance as yf

# Title for the App
st.markdown(
    "<h1 style='text-align: center;'>Black-Scholes Option Pricing Model for S&P 500 Equities</h1>",
    unsafe_allow_html=True
)

# Title for the sidebar
st.sidebar.title("BSM Inputs")

selected_equity = st.sidebar.selectbox(
    'Select an equity:',
    scrape_spy_tickers()
)

# Create yfinance Ticker object
sel_ticker = yf.Ticker(selected_equity)

# Calculate the current share price of the selected equity
cur_share_price = sel_ticker.history(period='1d')["Close"].iloc[-1]

# Calculate the current 30-day historical volatility for selected equity
cur_volatility = calc_historical_volatility(sel_ticker.history(period='30d'), 30)

# Placeholder for share price info
cur_share_price_placeholder = st.sidebar.empty()
cur_share_price_placeholder.write(f"**{selected_equity}** Current Share Price: **${cur_share_price:.2f}**")

# Default values for inputs
DEFAULT_VALUES = {
    "days_to_maturity": 30,
    "risk_free_rate_input": get_cur_risk_free_rate(),
    "strike_price_input": round(cur_share_price, 0),  # Default as rounded current share price
    "volatility": round(cur_volatility, 2)

}

# Initialize session state for all defaults
for key, value in DEFAULT_VALUES.items():
    if key not in st.session_state:
        st.session_state[key] = value


# Function to reset sidebar inputs to default values
def reset_inputs_to_default() -> None:
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value


if st.sidebar.button("Reset Below Inputs to Default"):
    reset_inputs_to_default()


# Strike Price Input
strike_price_input = st.sidebar.number_input(
    "Enter a Strike Price:",
    min_value=0.0,  # Minimum value of 0 (no strike below 0)
    step=0.1,  # Increment step
    format="%.2f",  # Display format,
    key='strike_price_input'
)

# Risk-free Rate Input
risk_free_rate_input = st.sidebar.number_input(
    "Enter Risk-Free Rate value or use 10yr T-Note Default",
    min_value=0.0,  # Minimum value of 0 (no strike below 0)
    step=0.01,  # Increment step
    format="%.2f",  # Display format,
    key='risk_free_rate_input'
)

# Days until maturity Input
days_to_maturity = st.sidebar.number_input(
    "Time to Maturity (in days):",
    min_value=1,  # Minimum 1 day
    step=1,  # Increment by 1 day
    key='days_to_maturity'
)

# Volatiltiy Input
volatility = st.sidebar.number_input(
    "Volatility:",
    min_value=0.0,  # Minimum 1 day
    step=.01,  # Increment by 1 day
    key='volatility'
)

st.sidebar.write("# ")
