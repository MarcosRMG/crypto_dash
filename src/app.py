# Data processing
import pandas as pd
from processing.crypto import portfolio_crypto
from processing.crypto import request_data

# Data viz
import streamlit as st
from streamlit_theme import st_theme
from data_viz.crypto import date_interval
from data_viz.crypto import plotly_time_series
import matplotlib.pyplot as plt
import seaborn as sns

# Analysis
import ta
from ta.trend import IchimokuIndicator
import plotly.express as px
import plotly.graph_objects as go

# Forecast
from forecast.crypto import auto_ts_forecast

# App utils
from data_viz.crypto import selected_language
# ============================================Streamlit settings=======================================
st.set_page_config(layout='wide')

# ============================================Data Input============================================
# --> Stocks Indexers
crypto_composition = portfolio_crypto('https://coinmarketcap.com/all/views/all/')

df_stock_crypto = pd.read_csv('./data/stocks/gold/crypto_trading.csv')
df_stock_crypto['Date'] = pd.to_datetime(df_stock_crypto['Date'])
df_stock_crypto.set_index('Date', inplace=True)
df_stock_crypto_month = df_stock_crypto.resample('ME').median()
df_stock_crypto_quarter = df_stock_crypto.resample('QE').median()

#QoQ
df_crypto_qoq = df_stock_crypto_quarter.pct_change(1).copy() * 100


def main():
    _, right_col = st.columns([10, 1]) 
    with right_col:
        lang = st.pills(label='Translate', options=['en', 'pt'], default='en')

    text_dict = selected_language(lang)
    
    # --> Company selection
    visualize_stocks = st.sidebar.selectbox('Crypto', crypto_composition['Symbol'].values)
    selected_ticker = crypto_composition[crypto_composition['Symbol'] == visualize_stocks]['Symbol'].to_list()[0]

    st.header(selected_ticker)

    # Data interval
    start_date, end_date = date_interval(screen='stock_price', language=lang)

    # ===================================Close Price===================================
    # Download data from Yahoo Finance (Close Price)
    selected_ticker_yf = selected_ticker + '-USD'
    df_stock_day = request_data(selected_ticker_yf, start_date)
    # Drop ticket index
    df_stock_day.columns = df_stock_day.columns.droplevel(1)
    df_stock_month = df_stock_day.resample('ME')[['Close']].median()
    df_stock_quarter = df_stock_day.resample('QE')[['Close']].median().iloc[:-1]    

    # RSI
    df_stock_day['rsi'] = ta.momentum.RSIIndicator(df_stock_day['Close'], window=5).rsi()

    # ICHIMOKU
    ichimoku = IchimokuIndicator(high=df_stock_day['High'], low=df_stock_day['Low'], window1=7, window2=21, window3=49)
    df_stock_day['tenkan_sen'] = ichimoku.ichimoku_conversion_line()
    df_stock_day['kijun_sen'] = ichimoku.ichimoku_base_line()
    df_stock_day['senkou_span_a'] = ichimoku.ichimoku_a()
    df_stock_day['senkou_span_b'] = ichimoku.ichimoku_b()

    # ====================================Forecast=====================================
    # Month
    df_stock_month.reset_index(inplace=True)
    df_stock_month['Date'] = pd.to_datetime(df_stock_month['Date'])
    try:
        market_model = auto_ts_forecast(df=df_stock_month, value_col='Close', date_col='Date',
                                            transformer_list=['SeasonalDifference', 'Detrend', 'DifferencedTransformer'],
                                            model_list=['ETS'], frequency='ME', exceptin_msg=text_dict['forecast'])

        market_forecast = market_model.predict()
        df_stock_month_forecast = pd.concat([df_stock_month,
                                             market_forecast.forecast.reset_index().rename(columns={'index': 'Date'})])
        # Quarter
        df_stock_quarter.reset_index(inplace=True)
        df_stock_quarter['Date'] = pd.to_datetime(df_stock_quarter['Date'])
        market_model_quarter = auto_ts_forecast(df=df_stock_quarter, value_col='Close', date_col='Date',
                                                transformer_list=['SeasonalDifference', 'Detrend', 'DifferencedTransformer'],
                                                model_list=['ETS'], frequency='QE', exceptin_msg=text_dict['forecast'])
        market_forecast_quarter = market_model_quarter.predict()
        df_stock_quarter_forecast = pd.concat([df_stock_quarter,
                                                  market_forecast_quarter.forecast.reset_index().rename(columns={'index': 'Date'})])

        # Data viz
        st.subheader(text_dict['headers'][1])
        plotly_time_series(time_series_list=[df_stock_month_forecast, df_stock_month_forecast.iloc[-2:],
                                   df_stock_day.reset_index(), df_stock_quarter_forecast],
                                   x_list=['Date', 'Date', 'Date', 'Date'], y_list=['Close', 'Close', 'Close', 'Close'],
                                   name_list=text_dict['close_price_plot'],
                                   y_label='$')
    except AttributeError:
        # Data viz
        st.subheader(text_dict['headers'][1])
        plotly_time_series(time_series_list=[df_stock_day.reset_index()],
                                   x_list=['Date'], y_list=['Close'],
                                   name_list=text_dict['close_price_plot'],
                                   y_label='$')


    col1, col2 = st.columns([0.5, 0.5])
    with col1:
        fig = px.line(df_stock_day['rsi'].iloc[-30:], title=text_dict['rsi_title'])
        fig.update_layout(yaxis_title='%')
        st.plotly_chart(fig)

    with col2:
        df_stock_qoq_temp = df_crypto_qoq[(df_crypto_qoq.index >= start_date) &
                                          (df_crypto_qoq.index <= end_date)].copy()

        fig = px.bar(df_stock_qoq_temp[[selected_ticker_yf]], title=text_dict['quarter_grapth_title'])
        fig.update_layout(yaxis_title='%')
        st.plotly_chart(fig)

    # =======================================Ichimoku===============================================
    theme = st_theme()
    background_color = theme['backgroundColor']
    text_color = theme['textColor']

    # Pltly
    fig = go.Figure()

    # Line plots
    df_stock_day_ichimoku = df_stock_day.iloc[-365:].copy()
    fig.add_trace(go.Scatter(x=df_stock_day_ichimoku.index, y=df_stock_day_ichimoku['Close'], mode='lines',
                             name='Close Price'))
    fig.add_trace(go.Scatter(x=df_stock_day_ichimoku.index, y=df_stock_day_ichimoku['tenkan_sen'], mode='lines',
                             name='Conversion Line'))
    fig.add_trace(go.Scatter(x=df_stock_day_ichimoku.index, y=df_stock_day_ichimoku['kijun_sen'], mode='lines',
                             name='Base Line', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=df_stock_day_ichimoku.index, y=df_stock_day_ichimoku['senkou_span_a'], mode='lines',
                             name='Senkou Span A', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df_stock_day_ichimoku.index, y=df_stock_day_ichimoku['senkou_span_b'], mode='lines',
                             name='Senkou Span B', line=dict(color='orange')))

    # Ichimoku Cloud fill areas (Senkou Span A >= B)
    mask_a_ge_b = df_stock_day_ichimoku['senkou_span_a'] >= df_stock_day_ichimoku['senkou_span_b']
    fig.add_trace(go.Scatter(
        x=df_stock_day_ichimoku.index[mask_a_ge_b],
        y=df_stock_day_ichimoku['senkou_span_a'][mask_a_ge_b],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df_stock_day_ichimoku.index[mask_a_ge_b],
        y=df_stock_day_ichimoku['senkou_span_b'][mask_a_ge_b],
        fill='tonexty',
        fillcolor='rgba(144,238,144,0.4)',  # lightgreen with transparency
        mode='lines',
        line=dict(width=0),
        name='Cloud (Bullish)'
    ))

    # Ichimoku Cloud fill areas (Senkou Span A < B)
    mask_a_lt_b = df_stock_day_ichimoku['senkou_span_a'] < df_stock_day_ichimoku['senkou_span_b']
    fig.add_trace(go.Scatter(
        x=df_stock_day_ichimoku.index[mask_a_lt_b],
        y=df_stock_day_ichimoku['senkou_span_a'][mask_a_lt_b],
        fill=None,
        mode='lines',
        line=dict(width=0),
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=df_stock_day_ichimoku.index[mask_a_lt_b],
        y=df_stock_day_ichimoku['senkou_span_b'][mask_a_lt_b],
        fill='tonexty',
        fillcolor='rgba(240,128,128,0.4)',  # lightcoral with transparency
        mode='lines',
        line=dict(width=0),
        name='Cloud (Bearish)'
    ))

    # Layout and theme
    fig.update_layout(
        title=dict(text='Ichimoku Cloud', x=0, font=dict(color=text_color)),
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        legend=dict(font=dict(color=text_color)),
        xaxis=dict(tickfont=dict(color=text_color), 
                   rangeslider=dict(visible=True), 
                   type="date"),
        yaxis=dict(tickfont=dict(color=text_color)),
        height=500
    )

    # Add grid lines
    fig.update_yaxes(showgrid=True, gridcolor='rgba(200,200,200,0.2)')

    st.plotly_chart(fig, use_container_width=True)


if __name__ == '__main__':
    main()
