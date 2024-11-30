import streamlit as st
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import datetime

# Set Streamlit page layout to wide
st.set_page_config(layout="wide")

def get_historical_bitcoin_prices():
    bitcoin = yf.Ticker("BTC-USD")
    today = datetime.date.today().strftime("%Y-%m-%d")
    hist = bitcoin.history(start="2016-07-09", end=today)
    return hist['Close']

def normalize_cycle_data(dates, prices, start_date):
    normalized_dates = [(date - start_date).days for date in dates]
    return normalized_dates, prices

st.title('Bitcoin Price Tracker')

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
