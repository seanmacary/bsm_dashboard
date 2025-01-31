import streamlit as st
from utils import (
    fetch_stock_data, compute_default_values,
    reset_inputs_to_default, scrape_spy_tickers, load_css
)
from plotting import (
    historical_stock_price_chart, generate_sensitivity_heatmap,
    generate_option_pnl
)
import pandas as pd
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
    step=1.0,
    key='price_shock_default_range',
)

# Slider for Volatility-Shock heatmap Axis
vol_shock_slider = st.sidebar.slider(
    'Select a range of volatility-shock values',
    round(cur_volatility * 0.5, 4),
    round(cur_volatility * 2.5, 4),
    st.session_state.vol_shock_default_range,
    key='vol_shock_default_range',
)

################# MAIN Section UI CODE #####################

# Title for the App
st.markdown(
    "<h1 style='text-align: center;'>Black-Scholes Option Pricing Model for S&P 500 Equities</h1>",
    unsafe_allow_html=True
)

st.write("## Historical Stock Price Chart")
# Historical Stock Price chart (1-yr)
st.plotly_chart(historical_stock_price_chart(selected_equity), use_container_width=True)

# Initialize BSM with provided input parameters
bsm = BlackScholesModel(
    S=cur_share_price,
    K=strike_price_input,
    T=days_to_maturity / 365,
    r=risk_free_rate_input / 100,
    sigma=volatility
)

# Call the function to load CSS
load_css("styles/metrics.css")

# Calculate Call and Put Options Prices
call_option_price = bsm.call_option_price()
put_option_price = bsm.put_option_price()

# Call and Put Option Containers
with st.container():
    st.write("## Option Price per Share")
    col1, col2 = st.columns([1, 1], gap="small")

    with col1:
        st.markdown(f"""
            <div class="metric-container metric-call">
                <div class="metric-label">Call Option Price per Share</div>
                <div class="metric-value">${call_option_price:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-container metric-put">
                <div class="metric-label">Put Option Price per Share</div>
                <div class="metric-value">${put_option_price:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.write(" ")
st.write("## Sensitivity Analysis: Option Pricing per Share")
st.write("Adjust the sidebar heatmap parameters to explore how option prices vary with changes in stock price and "
         "volatility.")


# Generate and display the heatmap
call_sensitivity_fig, put_sensitivity_fig = generate_sensitivity_heatmap(
    K=strike_price_input,
    T=days_to_maturity / 365,
    r=risk_free_rate_input / 100,
    price_range=price_shock_slider,
    vol_range=vol_shock_slider,
)

# Display side by side in Streamlit
col1, col2 = st.columns(2)
with col1:
    st.pyplot(call_sensitivity_fig)
with col2:
    st.pyplot(put_sensitivity_fig)

st.write("## Option Profit/Loss at Expiration")
st.write("**The below analysis considers 1 contract to consist of 100 shares of underlying**")
option_type = st.selectbox("Select Option Type", ["Call", "Put"])
num_contracts = st.number_input("Input number of Contracts Purchased", st.session_state.num_contracts, key='num_contracts')

fig = generate_option_pnl(
    option_type=option_type,
    strike_price=strike_price_input,
    premium_call=call_option_price,
    premium_put=put_option_price,
    stock_price_range=price_shock_slider,
    num_contracts=num_contracts
)
st.plotly_chart(fig)

# Create Data Table with Inputs
data = {
    "Option Type": [option_type],
    "Strike Price ($)": [f"{strike_price_input:.2f}"],
    "Total Premium Paid ($)": [f"{round(call_option_price * num_contracts * 100, 2) if option_type == 'Call' else round(put_option_price * num_contracts * 100, 2):.2f}"],
    "Break-Even Price ($)": [f"{strike_price_input + call_option_price if option_type == 'Call' else strike_price_input - put_option_price:.2f}"],
    "Max Profit ($)": ["Unlimited" if option_type == "Call" else f"{(strike_price_input - put_option_price) * num_contracts * 100:.2f}"],
    "Max Loss ($)": [f"{round(call_option_price * num_contracts * 100, 2) if option_type == 'Call' else round(put_option_price * num_contracts * 100, 2):.2f}"]
}

df = pd.DataFrame(data)
st.table(df)  # Display table above the plot
