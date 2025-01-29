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
