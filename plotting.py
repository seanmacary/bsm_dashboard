import streamlit as st
import yfinance as yf
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go

from black_scholes_model import BlackScholesModel


def historical_stock_price_chart(selected_equity: str):
    """
    Fetches historical stock data for the given equity and generates an interactive Plotly chart.
    """
    hist_stock_data = yf.Ticker(selected_equity).history(period='12mo')
    if hist_stock_data.empty:
        st.warning(f"No data available for {selected_equity}. Please try another stock.")
        return

    fig = px.line(
        hist_stock_data,
        x=hist_stock_data.index,  # Date as X-axis
        y="Close",  # Closing price as Y-axis
        title=f"{selected_equity} Historical Stock Price",
        labels={"Close": "Stock Price (USD)", "index": "Date"},
    )

    fig.update_layout(
        width=1200,  # Set width (adjustable)
        height=500,  # Set height (adjustable)
        xaxis_title="Date",
        yaxis_title="Stock Price (USD)",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        template="plotly_white",  # Clean white background theme
    )

    return fig


def generate_sensitivity_heatmap(K, T, r,  price_range, vol_range):
    """
    Generates heatmaps for Call and Put option prices based on stock price and volatility changes.
    """
    stock_prices = np.linspace(price_range[0], price_range[1], 8)
    volatilities = np.linspace(vol_range[0], vol_range[1], 8)

    call_prices = np.zeros((len(volatilities), len(stock_prices)))
    put_prices = np.zeros((len(volatilities), len(stock_prices)))

    for i, vol in enumerate(volatilities):
        for j, price in enumerate(stock_prices):
            bsm = BlackScholesModel(S=price, K=K, T=T, r=r, sigma=vol)
            call_prices[i, j] = bsm.call_option_price()
            put_prices[i, j] = bsm.put_option_price()

    # Plot Call Price Heatmap
    fig_call, ax_call = plt.subplots(figsize=(10, 8))
    sns.heatmap(call_prices, xticklabels=np.round(stock_prices, 2), yticklabels=np.round(volatilities, 2),
                annot=True, fmt=".2f", cmap="viridis", ax=ax_call, cbar_kws={'label': 'Premium Price per Share ($)'})
    ax_call.set_title('Call Option Prices per Share', fontsize=16)
    ax_call.set_xlabel('Stock Price')
    ax_call.set_ylabel('Volatility')

    # Plot Put Price Heatmap
    fig_put, ax_put = plt.subplots(figsize=(10, 8))
    sns.heatmap(put_prices, xticklabels=np.round(stock_prices, 2), yticklabels=np.round(volatilities, 2),
                annot=True, fmt=".2f", cmap="viridis", ax=ax_put, cbar_kws={'label': 'Premium Price per Share ($)'})
    ax_put.set_title('Put Option Prices per Share', fontsize=16)
    ax_put.set_xlabel('Stock Price')
    ax_put.set_ylabel('Volatility')

    return fig_call, fig_put


def generate_option_pnl(option_type, strike_price, premium_call, premium_put, stock_price_range, num_contracts):
    stock_prices = np.linspace(stock_price_range[0], stock_price_range[1], 100)
    if option_type == "Call":
        pnl = (np.maximum(stock_prices - strike_price, 0) - premium_call) * num_contracts * 100
        break_even = strike_price + premium_call
    else:
        pnl = (np.maximum(strike_price - stock_prices, 0) - premium_put) * num_contracts * 100
        break_even = strike_price - premium_put

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_prices, y=pnl, mode="lines", name=f"{option_type} Option P/L"))

    fig.add_vline(x=break_even, line=dict(color="red", dash="dash"), annotation_text=f"Break-even {option_type}",
                  annotation_position="top right")

    fig.update_layout(
        title=f"{option_type} Option Profit/Loss at Expiration",
        xaxis_title="Stock Price at Expiration",
        yaxis_title="Profit / Loss ($)",
        template="plotly_white"
    )
    return fig