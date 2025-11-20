import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from datetime import timedelta, datetime


def date_interval(screen: str, language: str, view: str = '', forecast=False):
    """
    Define the initial and final date selected to analyze data

    Parameters: view : String
                    Selected view to increase the initial date plus 365 days if "Seasonality and Trend"
                    was selected otherwise 365 before is predefined as default period

    Returns: initial_date : Pandas datetime
                Initial date

             end_date : Pandas datetime
                Final date
    """
    year_before_today = datetime.today() - timedelta(days=365 * 3)
    actual_year = datetime.today().year
    actual_month = datetime.today().month
    last_year = actual_year - 1
    initial_date: pd.Timestamp = None
    end_date: pd.Timestamp = None
    from utils.text_language.translator import selected_language

    text_dict = selected_language(language)

    if forecast:
        initial_date = pd.Timestamp(datetime(actual_year, actual_month + 1, 1))
        end_date = pd.Timestamp(datetime(actual_year + 1, actual_month, 1))
    else:
        if view == 'Seasonality and Trend':
            # Ensure 24 months to calculate seasonality
            # Stocks
            year_before_today -= timedelta(days=365)
            # Others
            last_year -= 1

        # Fix the day to montly indicators
        if screen == 'economic':
            initial_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][0],
                                                              datetime(last_year, actual_month - 1, 1)))
            end_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][1],
                                                          datetime(actual_year, actual_month - 2, 1)))
        elif screen == 'fund':
            initial_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][0],
                                                              datetime(last_year, actual_month - 1, 1)))
            end_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][1],
                                                          datetime(actual_year, actual_month - 1, 1)))
        elif screen == 'stock_price':
            initial_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][0], year_before_today))
            end_date = pd.Timestamp(st.sidebar.date_input(text_dict['date_filters'][1], datetime.today()))
    
    return initial_date, end_date


def plotly_time_series(time_series_list: list[pd.DataFrame], x_list: list[str], y_list: list[str], name_list: list[str],
                       y_label: str):
    fig = go.Figure()

    for idx in range(len(time_series_list)):
        fig.add_trace(go.Scatter(x=time_series_list[idx][x_list[idx]],
                                 y=time_series_list[idx][y_list[idx]],
                                 mode='lines',
                                 name=name_list[idx]))

    fig.update_layout(yaxis_title=y_label)

    st.plotly_chart(fig)


def selected_language(language: str):
    """
    Return a dictionary with text for selected language

    Returns : text_info: dict
                Dictionary of text for selected language
    """
    text_info = dict()

    if language == 'pt':
        text_info['top_menu'] = ['Mercado', 'Sazonalidade']
        text_info['market_menu'] = 'Mercado'
        text_info['stock_options'] = 'Ações'
        text_info['date_filters'] = ['Data Inicial', 'Data Final']
        text_info['headers'] = ['Lucros', 'Preço de Fechamento']
        text_info['close_price_plot'] = ['Média', 'Projeção', 'Mercado', 'Projeção Trimestral']
        text_info['ticket'] = 'Ativo'
        text_info['buy_month'] = 'Mês Compra'
        text_info['sell_month'] = 'Mês Venda'
        text_info['price_range'] = 'Variação Preço'
        text_info['confidence'] = 'Sazonalidade'
        text_info['quarter_grapth_title'] = 'Crescimento Trimestral (TsT)'
        text_info['rsi_title'] = 'Índice de Peso Relativo (RSI 5 dias)'
        text_info['forecast'] = 'Adicione pelo menos um ano de dados'
    elif language == 'en':
        text_info['market_menu'] = 'Market'
        text_info['stock_options'] = 'Stocks'
        text_info['date_filters'] = ['Start Date', 'End Date']
        text_info['headers'] = ['Net Income', 'Close Price']
        text_info['close_price_plot'] = ['Mean', 'Projection', 'Market', 'Quarter Projection']
        text_info['quarter_grapth_title'] = 'Grow QoQ'
        text_info['rsi_title'] = 'RSI 5 days'
        text_info['forecast'] = 'Add at least one year of data'

    return text_info