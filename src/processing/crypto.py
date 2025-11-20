import pandas as pd
import requests
from datetime import date
# Cache module
import streamlit as st
# Yahoo finance
import yfinance as yf


def portfolio_crypto(page_source: str):
    """
    Read page with crypto list

    Parameters: page_source : str
                    Web page with cripto names and symbols

    Return df : pd.DataFrame
                    Table with list Name and Symbol columns of cryptocurrencies with ticket name available
    """
    # Read page source and select table with name a symbol of cryptocurrencies
    r = requests.get(page_source).text
    df = pd.read_html(r)[2][['Name', 'Symbol']]
    df.dropna(inplace=True)
    
    return df


@st.cache_data
def request_data(selected_tickers: list, start_date: str, end_date: str = None):
    """
    Download historical financial data from Yahoo Finance about ticker negatiation

    Parameters: selected_tickers : List of string
                    Company tickers selected to download

                start_date: String
                    Initial date to download historical data

    Returns: DataFrame
                Pandas DataFrame with Open, High, Low, Close, Adj Close and Volume columns about selected tickers
                market negotiation
    """
    today = date.today()
    if end_date:
        df = yf.download(tickers=selected_tickers, start=start_date, end=end_date)
    else:
        df = yf.download(tickers=selected_tickers, start=start_date, end=today)
    return df