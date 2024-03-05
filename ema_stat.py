

from datetime import date, timedelta
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

def run_trading_strategy(df, tp_pct, sl_pct, pv):
    # Initialize portfolio value
    portfolio_value = pv

    # Initialize position state
    position = 'flat'

    # Initialize trading statistics
    long_trades = 0
    short_trades = 0
    long_profitable_trades = 0
    long_losing_trades = 0
    short_losing_trades = 0
    short_profitable_trades = 0
    exit_without_tp_sl_long_losing_trades = 0
    exit_without_tp_sl_short_losing_trades = 0
    total_profit = 0
    total_loss = 0
    
    # Lists to store trading information
    trades_data = {
        "Date": [],
        "Position": [],
        "Entry Price": [],
        "Exit Price": [],
        "Take Profit": [],
        "Stop Loss": [],
        "Portfolio Value": [],
        "reason": []
    }


    # Trading strategy conditions
    for i in range(2, len(df)):
        if position == 'flat':
            if (
                df['Close'][i] >= df['EMA21'][i] and
                df['Close'][i-1] > df['EMA21'][i-1] and
                df['Close'][i-2] > df['EMA21'][i-2] and
                df['Low'][i] <= df['EMA21'][i-1]
            ):
                position = 'long'
                entry_price = df['EMA21'][i]
                long_trades += 1

                # Calculate position size based on available capital
                position_size = portfolio_value / df['Close'][i]
                # Update portfolio value after buying
                portfolio_value -= position_size * entry_price
                
                # Store trade information
                trades_data["Date"].append(df.index[i])
                trades_data["Position"].append(position)
                trades_data["Entry Price"].append(entry_price)
                trades_data["Exit Price"].append(None)
                trades_data["Take Profit"].append(entry_price * (1 + tp_pct))
                trades_data["Stop Loss"].append(entry_price * (1 - sl_pct))
                trades_data["reason"].append(None)
                trades_data["Portfolio Value"].append(portfolio_value)
                
            elif (
                df['Close'][i] <= df['EMA21'][i] and
                df['Close'][i-1] < df['EMA21'][i-1] and
                df['Close'][i-2] < df['EMA21'][i-2] and
                df['High'][i] >= df['EMA21'][i-1]
            ):
                position = 'short'
                entry_price = df['EMA21'][i]
                short_trades += 1

                # Calculate position size based on available capital
                position_size = portfolio_value / df['Close'][i]
                # Update portfolio value after short selling
                portfolio_value += position_size * entry_price
                
                # Store trade information
                trades_data["Date"].append(df.index[i])
                trades_data["Position"].append(position)
                trades_data["Entry Price"].append(entry_price)
                trades_data["Exit Price"].append(None)
                trades_data["Take Profit"].append(entry_price * (1 - tp_pct))
                trades_data["Stop Loss"].append(entry_price * (1 + sl_pct))
                trades_data["reason"].append(None)
                trades_data["Portfolio Value"].append(portfolio_value)

        elif position == 'long':
            if df["High"][i] >= (entry_price * (1 + tp_pct)):
                position = 'flat'
                long_profitable_trades += 1
                total_profit += (df["High"][i] - entry_price)

                # Update portfolio value after selling
                portfolio_value += position_size * df["High"][i]
                
                # Update trade information
                trades_data["Exit Price"][-1] = df["High"][i]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "long_tp_hit"
                
            elif df["Low"][i] <= (entry_price * (1 - sl_pct)):
                position = 'flat'
                long_losing_trades += 1
                total_loss += (entry_price - df["Low"][i])

                # Update portfolio value after selling
                portfolio_value += position_size * df["Low"][i]
                
                # Update trade information
                trades_data["Exit Price"][-1] = df["Low"][i]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "long_sl_hit"
                
            elif df['High'][i] < df['EMA21'][i-1]:
                position = 'flat'
                exit_without_tp_sl_long_losing_trades += 1
                total_loss += (entry_price - df["Close"][i])

                # Update portfolio value after selling
                portfolio_value += position_size * df['EMA21'][i-1]
                
                
                # Update trade information
                trades_data["Exit Price"][-1] = df['EMA21'][i-1]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "long_na_tp_sl"

        elif position == 'short':
            if df["Low"][i] <= (entry_price * (1 - tp_pct)):
                position = 'flat'
                short_profitable_trades += 1
                total_profit += (entry_price - df["Low"][i])

                # Update portfolio value after covering
                portfolio_value -= position_size * df["Low"][i]
                
                # Update trade information
                trades_data["Exit Price"][-1] = df["Low"][i]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "short_tp_hit"
                
            elif df["High"][i] >= (entry_price * (1 + sl_pct)):
                position = 'flat'
                short_losing_trades += 1
                total_loss += (df["High"][i] - entry_price)

                # Update portfolio value after covering
                portfolio_value -= position_size * df["High"][i]
                
                # Update trade information
                trades_data["Exit Price"][-1] = df["High"][i]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "short_sl_hit"
                
            elif df['Low'][i] > df['EMA21'][i-1]:
                position = 'flat'
                exit_without_tp_sl_short_losing_trades += 1
                total_loss += (df["Close"][i] - entry_price)

                # Update portfolio value after covering
                portfolio_value -= position_size * df['EMA21'][i-1]
                
                # Update trade information
                trades_data["Exit Price"][-1] = df['EMA21'][i-1]
                trades_data["Portfolio Value"][-1] = portfolio_value
                trades_data["reason"][-1] = "short_na_tp_sl"

    # Create DataFrame from trades_data
    trades_df = pd.DataFrame(trades_data)
    
    # Return trading statistics, final portfolio value, and trades DataFrame
    return {
        "long_trades": long_trades,
        "short_trades": short_trades,
        "long_profitable_trades": long_profitable_trades,
        "long_losing_trades": long_losing_trades,
        "short_losing_trades": short_losing_trades,
        "short_profitable_trades": short_profitable_trades,
        "exit_without_tp_sl_long_losing_trades": exit_without_tp_sl_long_losing_trades,
        "exit_without_tp_sl_short_losing_trades": exit_without_tp_sl_short_losing_trades,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "initial_portfolio_value": pv,
        "final_portfolio_value": portfolio_value,
        "trades_data": trades_df
    }

# Streamlit App
st.title('Trading Strategy Streamlit App')

# Sidebar inputs
symbol = st.sidebar.text_input('Enter symbol (e.g., btc-usd):', 'btc-usd')
start_date = st.sidebar.date_input('Enter start date (YYYY-MM-DD):')
end_date = st.sidebar.date_input('Enter end date (YYYY-MM-DD):')
interval = st.sidebar.selectbox("Select time interval", ["5m", "15m", "30m", "1h", "1d"])
tp_pct = st.sidebar.number_input("input tp pct")
sl_pct = st.sidebar.number_input("input sl pct", key= 1)
pv = st.sidebar.number_input("enter portfolio value")
ema = st.sidebar.number_input("enter ema value ")
tp_pct = tp_pct/100
sl_pct = sl_pct/100
# Run trading strategy on button click
if st.sidebar.button('Run Strategy'):
    if interval == "5m" or interval == "15m" or interval == "30m":
        st.write(f"You have selected {interval} so the strategy will be tested for 60 days only due to the limitation of the yfinance library. Soon we will work towards this to facilitate the feature so you can test the strategy over a desired date range.")
        max_date = date.today()
        start_date = (max_date - timedelta(days=59)).strftime('%Y-%m-%d')
        end_date = max_date
        df = yf.download(symbol, start_date, end_date, interval=interval)
    elif interval == "1h":
        st.write(f"You have selected {interval} so the strategy will be tested for 730 days only due to the limitation of the yfinance library. Soon we will work towards this to facilitate the feature so you can test the strategy over a desired date range.")
        max_date = date.today()
        start_date = (max_date - timedelta(days=729)).strftime('%Y-%m-%d')
        end_date = max_date
        df = yf.download(symbol, start_date, end_date, interval=interval)
    else:
        df = yf.download(symbol, start_date, end_date, interval=interval)
    
    # Display historical data
    st.subheader("Historical Data")
    st.dataframe(df)
    # Calculate 21 EMA
    df['EMA21'] = df['Close'].ewm(span=ema, adjust=False).mean()

    # Run trading strategy
    strategy_results = run_trading_strategy(df, tp_pct, sl_pct, pv)

    # Display trading statistics
    st.subheader('Trading Statistics')
    st.write("Number of long trades:", strategy_results["long_trades"])
    st.write("Number of short trades:", strategy_results["short_trades"])
    st.write("Number of profitable long trades:", strategy_results["long_profitable_trades"])
    st.write("Number of profitable short trades:", strategy_results["short_profitable_trades"])
    st.write("Number of losing long trades:", strategy_results["long_losing_trades"])
    st.write("Number of losing short trades:", strategy_results["short_losing_trades"])
    st.write("Number of losing long trades without tp/sl:", strategy_results["exit_without_tp_sl_long_losing_trades"])
    st.write("Number of losing short trades without tp/sl:", strategy_results["exit_without_tp_sl_short_losing_trades"])
    st.write("Total profit:", strategy_results["total_profit"])
    st.write("Total loss:", strategy_results["total_loss"])
    st.write("Initial Portfolio Value:", strategy_results["initial_portfolio_value"])
    st.write("Final Portfolio Value:", strategy_results["final_portfolio_value"])
    # Access the trades DataFrame
    trades_df = strategy_results["trades_data"]

    # Display the trades DataFrame
    st.subheader('Trades Data')
    st.dataframe(trades_df)
