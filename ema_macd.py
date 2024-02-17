import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
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

# Plotting candlestick chart using Plotly
fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

# Display the candlestick chart
st.plotly_chart(fig)

# Plotting MACD
st.write("## MACD Indicator")
fig.add_trace(go.Scatter(x=macd_line.index, y=macd_line, mode='lines', name='MACD Line', line=dict(color='orange')))
fig.add_trace(go.Scatter(x=signal_line.index, y=signal_line, mode='lines', name='Signal Line', line=dict(color='green')))

# Plot the histogram with different shades for positive and negative values
for i in range(1, len(macd_histogram)):
    if macd_histogram.iloc[i] >= 0:
        color = 'darkgreen' if macd_histogram.iloc[i] >= macd_histogram.iloc[i - 1] else 'lightgreen'
    else:
        color = 'darkred' if macd_histogram.iloc[i] <= macd_histogram.iloc[i - 1] else 'lightcoral'

    fig.add_trace(go.Bar(x=[macd_histogram.index[i]], y=[macd_histogram.iloc[i]], marker_color=color, opacity=0.5))

fig.update_layout(title='MACD Indicator', xaxis_title='Date', yaxis_title='Price', showlegend=True)
st.plotly_chart(fig)
