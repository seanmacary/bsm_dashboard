import streamlit as st
from utils import (
    fetch_stock_data, compute_default_values,
    reset_inputs_to_default, scrape_spy_tickers
)
from plotting import historical_stock_price_chart
from black_scholes_model import BlackScholesModel


# Page configuration
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model for S&P 500 Equities",
    layout="wide",
    initial_sidebar_state="expanded")

################# SIDEBAR Section UI CODE #####################

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
cur_share_price, cur_volatility = fetch_stock_data(selected_equity)

# Store default values in session state
if "default_values" not in st.session_state or st.session_state.reset_flag:
    st.session_state.default_values = compute_default_values(cur_share_price, cur_volatility)
    st.session_state.update(st.session_state.default_values)
    st.session_state.reset_flag = False
    st.rerun()

# Placeholder for share price info
cur_share_price_placeholder = st.sidebar.empty()
cur_share_price_placeholder.write(f"**{selected_equity}** Current Share Price: **${cur_share_price:.2f}**")

# Sidebar Inputs
if st.sidebar.button("Reset Below Inputs to Default"):
    reset_inputs_to_default()

# Strike Price Input
strike_price_input = st.sidebar.number_input(
    "Enter a Strike Price:",
    min_value=0.0,  # Minimum value of 0 (no strike below 0)
    step=1.0,  # Increment step
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

# Slider for Price-Shock heatmap Axis
price_shock_slider = st.sidebar.slider(
    'Select a range of price-shock values',
    round(cur_share_price * 0.7, 0),
    round(cur_share_price * 1.3, 0),
    st.session_state.price_shock_default_range,
    key='price_shock_default_range',
)

# Slider for Volatility-Shock heatmap Axis
vol_shock_slider = st.sidebar.slider(
    'Select a range of volatility-shock values',
    round(cur_volatility * 0.5, 4),
    round(cur_volatility * 1.5, 4),
    st.session_state.vol_shock_default_range,
    key='vol_shock_default_range',
)

################# MAIN Section UI CODE #####################

# Title for the App
margins_css = """
    <style>
        .main > div {
            padding-left: 0rem;
            padding-right: 0rem;
        }
    </style>
"""

st.markdown(margins_css, unsafe_allow_html=True)
st.markdown(
    "<h1 style='text-align: center;'>Black-Scholes Option Pricing Model for S&P 500 Equities</h1>",
    unsafe_allow_html=True
)

# Historical Stock Price chart (1-yr)
st.plotly_chart(historical_stock_price_chart(selected_equity), use_container_width=True)

# Initialize BSM with provided input parameters
bsm = BlackScholesModel(
    S=cur_share_price,
    K=strike_price_input,
    T=days_to_maturity / 365,
    r=risk_free_rate_input/100,
    sigma=volatility
)

# Create a new container with two columns
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Call Option Price")
        st.metric(label="Current Price", value=f"${bsm.call_option_price():.2f}")

    with col2:
        st.subheader("Put Option Price")
        st.metric(label="Current Price", value=f"${bsm.put_option_price():.2f}")


