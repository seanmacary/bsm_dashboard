# Black-Scholes Model Option Pricing Streamlit App

## Overview

This project is a Streamlit-based web application that allows users to estimate Call and Put option prices for S&P 500 equities using the **Black-Scholes Model (BSM)**. The Black-Scholes Model is a mathematical framework used to determine the theoretical price of European-style options by considering factors such as the underlying stock price, strike price, time to expiration, risk-free interest rate, and market volatility. Widely used in financial markets, BSM helps traders and investors assess fair option pricing, manage risk, and develop trading strategies based on expected price movements. The app dynamically fetches stock price data, calculates volatility, and provides an interactive interface for financial analysis.
## Features

- **S&P 500 Stock Selection**: Fetches a list of **S&P 500 tickers** dynamically.
- **Real-Time Stock Data**: Uses **Yahoo Finance (yfinance)** to retrieve **current stock prices** and **historical volatility**.
- **Black-Scholes Model Implementation**: Computes **Call and Put option prices** based on user-defined inputs.
- **Historical Stock Price Chart**: Visualizes **1-year stock performance** with **Plotly charts**.
- **Customizable Inputs**: Allows users to adjust parameters such as:
  - **Strike Price**
  - **Risk-Free Rate** (Default: 10-Year Treasury Note Yield)
  - **Days to Maturity**
  - **Volatility**
- **Interactive Sensitivity Analysis**: Price and volatility shock sliders to analyze option price fluctuations.
- **Option P&L Chart**:
  - Generates **profit & loss (P&L) curves** for **Call and Put options**  
  - Helps visualize potential **option strategy outcomes**
- **Stylized UI**: Custom CSS for **enhanced UI/UX**.

---

## Installation & Setup

### Prerequisites

Ensure you have Python installed. Install the required dependencies and launch the application using:

```bash
pip install -r requirements.txt

streamlit run main.py

