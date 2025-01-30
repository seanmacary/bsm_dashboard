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

# Initialize session state for tracking the currently selected equity
if "selected_equity" not in st.session_state:
    st.session_state.selected_equity = None

# Initialize session state for reset flag used to reload app when selected equity changes
if "reset_flag" not in st.session_state:
    st.session_state.reset_flag = False

# Equity Dropdown (contains list of all S&P500 Tickers)
selected_equity = st.sidebar.selectbox(
    'Select an equity:',
    scrape_spy_tickers()
)

# If ticker has changed, trigger reset logic
if selected_equity != st.session_state.selected_equity:
    st.session_state.selected_equity = selected_equity
    st.session_state.reset_flag = True
    st.rerun()

# Fetch Stock Data
sel_ticker = yf.Ticker(selected_equity)
cur_share_price = sel_ticker.history(period='1d')["Close"].iloc[-1]
cur_volatility = calc_historical_volatility(sel_ticker.history(period='30d'), 30)

# Placeholder for share price info
cur_share_price_placeholder = st.sidebar.empty()
cur_share_price_placeholder.write(f"**{selected_equity}** Current Share Price: **${cur_share_price:.2f}**")

# Default values for inputs
DEFAULT_VALUES = {
    "days_to_maturity": 30,
    "risk_free_rate_input": get_cur_risk_free_rate(),
    "strike_price_input": round(cur_share_price, 0),  # Default as rounded current share price
    "volatility": round(cur_volatility, 2),
    "price_shock_default_range":  (round(cur_share_price * 0.9, 0),
                                   round(cur_share_price * 1.1, 0)),
    "vol_shock_default_range": (round(cur_volatility * 0.95, 4),
                                round(cur_volatility * 1.05, 4)),
}

# Reset inputs when reset_flag is set
if st.session_state.reset_flag:
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value
    st.session_state.reset_flag = False  # Clear flag after resetting
    st.rerun()


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

st.sidebar.write("# Heatmap Parameters")

# Price shock range calculations
price_shock_percentage = 0.3
price_shock_min = round(cur_share_price * (1 - price_shock_percentage), 0)
price_shock_max = round(cur_share_price * (1 + price_shock_percentage), 0)

# Slider for Price-Shock heatmap Axis
price_shock_slider = st.sidebar.slider(
    'Select a range of price-shock values',
    price_shock_min, price_shock_max,
    st.session_state.price_shock_default_range,
    key='price_shock_default_range',
)

vol_shock_percentage = 0.50
vol_shock_min = round(cur_volatility * (1 - vol_shock_percentage), 4)
vol_shock_max = round(cur_volatility * (1 + vol_shock_percentage), 4)

# Slider for Volatility-Shock heatmap Axis
vol_shock_slider = st.sidebar.slider(
    'Select a range of volatility-shock values',
    vol_shock_min, vol_shock_max,
    st.session_state.vol_shock_default_range,
    key='vol_shock_default_range',
)
