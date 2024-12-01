import streamlit as st
import matplotlib.pyplot as plt
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
    dates = list(historical_prices.index)  # Dates are pandas.Timestamp objects
    prices = list(historical_prices.values)

    # Define Bitcoin halving dates
    halving = ['2016-07-09', '2020-05-11', '2024-04-19']
    # Convert halving dates to pandas.Timestamp and ensure they are tz-naive
    halving_dates = [pd.Timestamp(date).tz_localize(None) for date in halving]

    # Ensure all dates in the dataset are tz-naive
    dates = [pd.Timestamp(date).tz_localize(None) for date in dates]

    # Split the data based on halving dates
    def split_data_by_halving(dates, prices, halving_dates):
        split_data = []
        start_index = 0
        for halving_date in halving_dates:
            end_index = next((i for i, date in enumerate(dates) if date >= halving_date), len(dates))
            # Ensure that the current segment isn't empty
            if start_index < end_index:
                split_data.append((dates[start_index:end_index], prices[start_index:end_index]))
            start_index = end_index
        # Add the remaining data after the last halving date
        if start_index < len(dates):
            split_data.append((dates[start_index:], prices[start_index:]))
        return split_data

    split_data = split_data_by_halving(dates, prices, halving_dates)

    # Plot the overlapping data with normalization
    fig, ax = plt.subplots(figsize=(20, 10))  # Adjust the figure size
    for i, (split_dates, split_prices) in enumerate(split_data):
        if not split_dates:  # Skip empty cycles
            continue
        start_date = split_dates[0]
        normalized_dates, normalized_prices = normalize_cycle_data(split_dates, split_prices, start_date)
        
        # Normalize prices by dividing each price by the first price in the cycle
        normalized_prices = [price / split_prices[0] for price in split_prices]
        
        ax.plot(normalized_dates, normalized_prices, label=f'Halving {i+2}' +' ('+ halving[i]+ ')')  # Removed marker='o'

    ax.set_title('Bitcoin Price Over Time (Overlapping Halving Cycles, Normalized)')
    ax.set_xlabel('Days Since Cycle Start')
    ax.set_ylabel('Price Ratio (Relative to Start)')
    ax.legend()
    ax.grid()
    st.pyplot(fig)
    st.write("---")  # Add a separator between the plots

def bitcoin_ethereum_ratio_plot():
    def get_historical_prices(ticker, start_date):
        asset = yf.Ticker(ticker)
        today = datetime.date.today().strftime("%Y-%m-%d")
        hist = asset.history(start=start_date, end=today)
        return hist['Close']

    # Fetch historical Bitcoin and Ethereum prices
    bitcoin_prices = get_historical_prices("BTC-USD", "2016-07-09")
    ethereum_prices = get_historical_prices("ETH-USD", "2016-07-09")

    # Align the dates of both datasets
    combined_data = pd.concat([bitcoin_prices, ethereum_prices], axis=1, keys=['Bitcoin', 'Ethereum']).dropna()

    # Define Bitcoin halving dates
    halving = ['2016-07-09', '2020-05-11', '2024-04-19']
    halving_dates = [pd.Timestamp(date).tz_localize(None) for date in halving]

    # Ensure all dates in the dataset are tz-naive
    combined_data.index = [pd.Timestamp(date).tz_localize(None) for date in combined_data.index]

    # Split the data based on halving dates
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

    # Plot each halving cycle in a separate graph
    for i, split_df in enumerate(split_data):
        if split_df.empty:
            continue
        fig, ax = plt.subplots(figsize=(20, 10))
        start_date = split_df.index[0]
        normalized_dates = [(date - start_date).days for date in split_df.index]
        
        # Normalize prices by dividing each price by the first price in the cycle
        normalized_bitcoin_prices = split_df['Bitcoin'] / split_df['Bitcoin'].iloc[0]
        normalized_ethereum_prices = split_df['Ethereum'] / split_df['Ethereum'].iloc[0]
        
        ax.plot(normalized_dates, normalized_bitcoin_prices, label='Bitcoin')
        ax.plot(normalized_dates, normalized_ethereum_prices, label='Ethereum')

        ax.set_title(f'Bitcoin and Ethereum Price Over Time (Halving {i+2}, Normalized)')
        ax.set_xlabel('Days Since Cycle Start')
        ax.set_ylabel('Price Ratio (Relative to Start)')
        ax.legend()
        ax.grid()
        st.pyplot(fig)
        st.write("---")

# Create a dropdown menu for the user to choose which chart to display
chart_option = st.selectbox('Select Chart', ('Bitcoin Cycle Plot', 'Bitcoin-Ethereum Ratio Plot'))

if chart_option == 'Bitcoin Cycle Plot':
    bitcoin_cycle_plot()
elif chart_option == 'Bitcoin-Ethereum Ratio Plot':
    bitcoin_ethereum_ratio_plot()