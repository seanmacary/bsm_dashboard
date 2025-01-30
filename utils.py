import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np


@st.cache_data  # Caches data to prevent re-running on every reload
def scrape_spy_tickers() -> list[str]:
    """Scrapes S&P 500 tickers from Wikipedia and caches the result."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    sp500_table = tables[0]
    tickers = sp500_table["Symbol"].tolist()
    return tickers


@st.cache_data
def get_cur_risk_free_rate() -> float:
    """Gets the current yield on 10-yr T-Note as proxy for risk-free rate"""
    ten_year_treasury = yf.Ticker("^TNX")
    yield_rate = ten_year_treasury.history(period="1d")["Close"].iloc[-1]
    return yield_rate


def calc_historical_volatility(stock_data, window: int = 252) -> float:
    log_returns = np.log(stock_data['Close'] / stock_data['Close'].shift(1))
    volatility = np.sqrt(window) * log_returns.std()
    return volatility


def fetch_stock_data(selected_equity: str):
    """Fetch stock price and volatility data for the selected equity."""
    sel_ticker = yf.Ticker(selected_equity)
    cur_share_price = sel_ticker.history(period='1d')["Close"].iloc[-1]
    cur_volatility = calc_historical_volatility(sel_ticker.history(period='30d'), 30)
    return cur_share_price, cur_volatility


def compute_default_values(cur_share_price: float, cur_volatility: float) -> dict:
    """Compute the default input values dynamically."""
    return {
        "days_to_maturity": 30,
        "risk_free_rate_input": get_cur_risk_free_rate(),
        "strike_price_input": round(cur_share_price, 0),
        "volatility": round(cur_volatility, 2),
        "price_shock_default_range": (
            round(cur_share_price * 0.9, 0),
            round(cur_share_price * 1.1, 0),
        ),
        "vol_shock_default_range": (
            round(cur_volatility * 0.95, 4),
            round(cur_volatility * 1.05, 4),
        ),
    }


def reset_inputs_to_default() -> None:
    """Reset all sidebar input values to their default state."""
    for key, value in st.session_state.default_values.items():
        st.session_state[key] = value


def load_css(file_name: str):
    """Reads and injects CSS file into Streamlit."""
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

