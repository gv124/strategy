# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import yfinance as yf
# import mplfinance as mpf

# def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
#     short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()    # Calculate short-term exponential moving average (EMA)
#     long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()      # Calculate long-term exponential moving average (EMA)
#     macd_line = short_ema - long_ema                                         # Calculate MACD line
#     signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()     # Calculate Signal line (9-day EMA of MACD line)
#     macd_histogram = macd_line - signal_line                                 # Calculate MACD Histogram
#     return macd_line, signal_line, macd_histogram

# def get_data(symbol, start, end, interval):
#     data = yf.download(symbol, start=start, end=end, interval=interval)
#     return data

# symbol = "btc-usd"
# start = "2024-01-01"
# end = "2024-02-16"
# interval = "1d"
# df = get_data(symbol, start, end, interval)

# # Plotting candlestick chart
# mpf.plot(df, type='candle', style='nightclouds', title='Candlestick Chart', ylabel='Price')

# # Calculate MACD
# macd_line, signal_line, macd_histogram = calculate_macd(df)

# # Set the background color to dark
# plt.figure(figsize=(10, 6), facecolor='black')

# # Plotting
# plt.plot(macd_line.index, macd_line, label='MACD Line', color='orange')
# plt.plot(signal_line.index, signal_line, label='Signal Line', color='green')

# # Plot the histogram with different shades for positive and negative values
# for i in range(1, len(macd_histogram)):
#     if macd_histogram.iloc[i] >= 0:
#         color = 'darkgreen' if macd_histogram.iloc[i] >= macd_histogram.iloc[i - 1] else 'lightgreen'
#         plt.bar(macd_histogram.index[i], macd_histogram.iloc[i], color=color, alpha=0.5)
#     else:
#         color = 'darkred' if macd_histogram.iloc[i] <= macd_histogram.iloc[i - 1] else 'lightcoral'
#         plt.bar(macd_histogram.index[i], macd_histogram.iloc[i], color=color, alpha=0.5)

# plt.title('MACD Indicator')
# plt.xlabel('Date')
# plt.ylabel('Price')
# plt.legend()
# plt.show()


import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
from mplfinance.plotting import plotly as mpf_plotly
import plotly.express as px

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    macd_histogram = macd_line - signal_line
    return macd_line, signal_line, macd_histogram

def get_data(symbol, start, end, interval):
    data = yf.download(symbol, start=start, end=end, interval=interval)
    return data

# Streamlit App
st.title('Candlestick Chart with MACD Indicator')

# Sidebar for user input
symbol = st.sidebar.text_input('Enter Stock Symbol (e.g., AAPL)', 'AAPL')
start_date = st.sidebar.date_input('Select Start Date', pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input('Select End Date', pd.to_datetime("2024-02-16"))

# Fetch data
df = get_data(symbol, start_date, end_date, "1d")

# Calculate MACD
macd_line, signal_line, macd_histogram = calculate_macd(df)

# Plotting candlestick chart using mplfinance with plotly backend
fig, ax = mpf_plotly.plot(df, type='candle', style='nightclouds', title='Candlestick Chart', ylabel='Price')

# Display the candlestick chart
st.plotly_chart(fig)

# Plotting MACD
st.write("## MACD Indicator")
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(macd_line.index, macd_line, label='MACD Line', color='orange')
ax.plot(signal_line.index, signal_line, label='Signal Line', color='green')

# Plot the histogram with different shades for positive and negative values
for i in range(1, len(macd_histogram)):
    if macd_histogram.iloc[i] >= 0:
        color = 'darkgreen' if macd_histogram.iloc[i] >= macd_histogram.iloc[i - 1] else 'lightgreen'
        ax.bar(macd_histogram.index[i], macd_histogram.iloc[i], color=color, alpha=0.5)
    else:
        color = 'darkred' if macd_histogram.iloc[i] <= macd_histogram.iloc[i - 1] else 'lightcoral'
        ax.bar(macd_histogram.index[i], macd_histogram.iloc[i], color=color, alpha=0.5)

ax.set_title('MACD Indicator')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.legend()

# Display the MACD plot
st.pyplot(fig)
