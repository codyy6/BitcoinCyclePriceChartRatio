import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import datetime

def normalize_cycle_data(dates, prices, start_date):
    normalized_dates = [(date - start_date).days for date in dates]
    return normalized_dates, prices

# Set Streamlit page layout to wide
st.set_page_config(layout="wide")
st.title('Bitcoin Price Tracker')

def bitcoin_cycle_plot():
    def get_historical_bitcoin_prices():
        bitcoin = yf.Ticker("BTC-USD")
        today = datetime.date.today().strftime("%Y-%m-%d")
        hist = bitcoin.history(start="2016-07-09", end=today)
        return hist['Close']

    # Fetch historical Bitcoin prices
    historical_prices = get_historical_bitcoin_prices()
    dates = list(historical_prices.index)
    prices = list(historical_prices.values)

    # Define Bitcoin halving dates
    halving = ['2016-07-09', '2020-05-11', '2024-04-19']
    halving_dates = [pd.Timestamp(date).tz_localize(None) for date in halving]

    dates = [pd.Timestamp(date).tz_localize(None) for date in dates]

    # Split data based on halving dates
    def split_data_by_halving(dates, prices, halving_dates):
        split_data = []
        start_index = 0
        for halving_date in halving_dates:
            end_index = next((i for i, date in enumerate(dates) if date >= halving_date), len(dates))
            if start_index < end_index:
                split_data.append((dates[start_index:end_index], prices[start_index:end_index]))
            start_index = end_index
        if start_index < len(dates):
            split_data.append((dates[start_index:], prices[start_index:]))
        return split_data

    split_data = split_data_by_halving(dates, prices, halving_dates)

    # Create an interactive Plotly figure
    fig = go.Figure()
    for i, (split_dates, split_prices) in enumerate(split_data):
        if not split_dates:
            continue
        start_date = split_dates[0]
        normalized_dates, _ = normalize_cycle_data(split_dates, split_prices, start_date)

        # Normalize prices by dividing each price by the first price in the cycle
        normalized_prices = [price / split_prices[0] for price in split_prices]

        fig.add_trace(go.Scatter(
            x=normalized_dates,
            y=normalized_prices,
            mode='lines',
            name=f'Halving {i+2} ({halving[i]})',
            hovertemplate='<b>Day:</b> %{x}<br><b>Price:</b> %{y:.2f}'
        ))

    fig.update_layout(
        title="Bitcoin Price Over Time (Overlapping Halving Cycles, Normalized)",
        xaxis_title="Days Since Cycle Start",
        yaxis_title="Price (Relative to Start Price)",
        template="plotly_white",
        legend_title="Halving Cycles"
    )

    st.plotly_chart(fig)

def bitcoin_ethereum_ratio_plot():
    def get_historical_prices(ticker, start_date):
        asset = yf.Ticker(ticker)
        today = datetime.date.today().strftime("%Y-%m-%d")
        hist = asset.history(start=start_date, end=today)
        return hist['Close']

    bitcoin_prices = get_historical_prices("BTC-USD", "2016-07-09")
    ethereum_prices = get_historical_prices("ETH-USD", "2016-07-09")

    combined_data = pd.concat([bitcoin_prices, ethereum_prices], axis=1, keys=['Bitcoin', 'Ethereum']).dropna()

    halving = ['2016-07-09', '2020-05-11', '2024-04-19']
    halving_dates = [pd.Timestamp(date).tz_localize(None) for date in halving]

    combined_data.index = [pd.Timestamp(date).tz_localize(None) for date in combined_data.index]

    def split_data_by_halving(data, halving_dates):
        split_data = []
        start_index = 0
        for halving_date in halving_dates:
            end_index = next((i for i, date in enumerate(data.index) if date >= halving_date), len(data))
            if start_index < end_index:
                split_data.append(data.iloc[start_index:end_index])
            start_index = end_index
        if start_index < len(data):
            split_data.append(data.iloc[start_index:])
        return split_data

    split_data = split_data_by_halving(combined_data, halving_dates)

    for i, split_df in enumerate(split_data):
        if split_df.empty:
            continue
        fig = go.Figure()
        start_date = split_df.index[0]
        normalized_dates = [(date - start_date).days for date in split_df.index]

        normalized_bitcoin_prices = split_df['Bitcoin'] / split_df['Bitcoin'].iloc[0]
        normalized_ethereum_prices = split_df['Ethereum'] / split_df['Ethereum'].iloc[0]

        fig.add_trace(go.Scatter(
            x=normalized_dates,
            y=normalized_bitcoin_prices,
            mode='lines',
            name='Bitcoin',
            hovertemplate='<b>Day:</b> %{x}<br><b>Price:</b> %{y:.2f}'
        ))
        fig.add_trace(go.Scatter(
            x=normalized_dates,
            y=normalized_ethereum_prices,
            mode='lines',
            name='Ethereum',
            hovertemplate='<b>Day:</b> %{x}<br><b>Price:</b> %{y:.2f}'
        ))

        fig.update_layout(
            title=f"Bitcoin and Ethereum Price Over Time (Halving {i+2}, Normalized)",
            xaxis_title="Days Since Cycle Start",
            yaxis_title="Price Ratio (Relative to Start)",
            template="plotly_white",
            legend_title="Assets"
        )

        st.plotly_chart(fig)

# Create a dropdown menu for the user to choose which chart to display
chart_option = st.selectbox('Select Chart', ('Bitcoin Cycle Plot', 'Bitcoin-Ethereum Ratio Plot'))

if chart_option == 'Bitcoin Cycle Plot':
    bitcoin_cycle_plot()
elif chart_option == 'Bitcoin-Ethereum Ratio Plot':
    bitcoin_ethereum_ratio_plot()
