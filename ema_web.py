import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Function to execute trading strategy
def execute_strategy(df, ema_v, tp, sl):
    ema = ema_v
    position_type = "na"
    status = "not in trade"
    
    tp = tp/100  # 1%
    sl = sl/100 # 5%
    new_short_tp = 0.005
    new_short_sl = 0.03
    
    # Stats
    long_trades = 0
    short_trades = 0
    num_trades_hit_long_tp = 0
    num_trades_hit_short_tp = 0
    long_sl_hit = 0
    short_sl_hit = 0
    long_exit_without_tp_sl = 0
    short_exit_without_tp_sl = 0
    
    portfolio_value = 100
    leverage = 1
    portfolio = portfolio_value
    p_array = []
    
    trades_data = {
        "Date": [],
        "Position": [],
        "Entry Price": [],
        "Exit Price": [],
        "Take Profit": [],
        "Stop Loss": [],
        "Portfolio Value": [],
        "Reason": [],
        "exit_date": []
    }

    df['EMA21'] = df['Close'].ewm(span=ema, adjust=False).mean()

    for i in range(2, len(df)):
        if status == "not in trade":
            # Condition for long trades
            if (
                df['Close'][i] >= df['EMA21'][i]
                and df['Close'][i - 1] > df['EMA21'][i - 1]
                and df['Close'][i - 2] > df['EMA21'][i - 2]
                and df['Low'][i] <= df['EMA21'][i - 1]
            ):
                position_type = "Long trade"
                entry_price = df['EMA21'][i - 1]
                long_tp = entry_price + (entry_price * tp)
                long_sl = entry_price - (entry_price * sl)
                long_trades += 1
                status = "in trade"

                trades_data["Date"].append(df.index[i])
                trades_data["Position"].append(position_type)
                trades_data["Entry Price"].append(entry_price)
                trades_data["Exit Price"].append(None)
                trades_data["Take Profit"].append(long_tp)
                trades_data["Stop Loss"].append(long_sl)
                trades_data["Reason"].append(None)
                trades_data["Portfolio Value"].append(portfolio)
                trades_data["exit_date"].append(None)

            # Condition for short trades
            elif (
                df["Open"][i] <= df['EMA21'][i]
                and df['Open'][i - 1] < df['EMA21'][i - 1]
                and df['Open'][i - 2] < df['EMA21'][i - 2]
                and df['High'][i] >= df['EMA21'][i - 1]
            ):
                position_type = "Short trade"
                entry_price = df['EMA21'][i - 1]
                short_tp = entry_price - (entry_price * new_short_tp)
                short_sl = entry_price + (entry_price * new_short_sl)
                short_trades += 1
                status = "in trade"

                trades_data["Date"].append(df.index[i])
                trades_data["Position"].append(position_type)
                trades_data["Entry Price"].append(entry_price)
                trades_data["Exit Price"].append(None)
                trades_data["Take Profit"].append(short_tp)
                trades_data["Stop Loss"].append(short_sl)
                trades_data["Reason"].append(None)
                trades_data["Portfolio Value"].append(portfolio)
                trades_data["exit_date"].append(None)

        elif status == "in trade":
            # Long TP
            if position_type == "Long trade":
                if long_tp >= df["High"][i]:
                    status = "not in trade"
                    num_trades_hit_long_tp += 1
                    portfolio += portfolio_value * tp * leverage
                    p_array.append(portfolio)
                    trades_data["Exit Price"][-1] = long_tp
                    trades_data["Reason"][-1] = "long_tp_hit"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

                # Long SL
                elif long_sl >= df["Low"][i]:
                    status = "not in trade"
                    long_sl_hit += 1
                    portfolio -= portfolio_value * sl * leverage
                    p_array.append(portfolio)
                    trades_data["Exit Price"][-1] = long_sl
                    trades_data["Reason"][-1] = "long_sl_hit"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

                # Exit without TP and SL
                elif df['EMA21'][i - 1] > df["High"][i]:
                    status = "not in trade"
                    long_exit_without_tp_sl += 1
                    loss = ((df["Close"][i] - entry_price) / entry_price)
                    portfolio += portfolio_value * loss * leverage
                    p_array.append(portfolio)
                    trades_data["Exit Price"][-1] = df["Close"][i]
                    trades_data["Reason"][-1] = "third_condition"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

            # Short TP and SL
            elif position_type == "Short trade":
                if short_tp >= df["Low"][i]:
                    status = "not in trade"
                    num_trades_hit_short_tp += 1
                    portfolio += portfolio_value * new_short_tp * leverage
                    trades_data["Exit Price"][-1] = short_tp
                    trades_data["Reason"][-1] = "short_tp_hit"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

                elif short_sl <= df["High"][i]:
                    status = "not in trade"
                    short_sl_hit += 1
                    portfolio -= portfolio_value * new_short_sl * leverage
                    trades_data["Exit Price"][-1] = short_sl
                    trades_data["Reason"][-1] = "short_sl_hit"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

                elif df['EMA21'][i - 1] < df["Low"][i]:
                    status = "not in trade"
                    short_exit_without_tp_sl += 1
                    loss = ((df["High"][i] - entry_price) / entry_price)
                    portfolio -= portfolio_value * loss * leverage
                    trades_data["Exit Price"][-1] = df["Close"][i]
                    trades_data["Reason"][-1] = "third_condition"
                    trades_data["Portfolio Value"][-1] = portfolio
                    trades_data["exit_date"][-1] = df.index[i]

    st.write("Num of long trades executed:", long_trades)
    st.write("Num long trades exited by hitting TP:", num_trades_hit_long_tp)
    st.write("Long SL hit:", long_sl_hit)
    st.write("Exit without TP and SL for long trades:", long_exit_without_tp_sl)
    st.write("Portfolio for long trades:", portfolio)

    st.write("\nShort trades:")
    st.write("Num of short trades executed:", short_trades)
    st.write("Num short trades exited by hitting TP:", num_trades_hit_short_tp)
    st.write("Short SL hit:", short_sl_hit)
    st.write("Exit without TP and SL for short trades:", short_exit_without_tp_sl)
    st.write("Portfolio for short trades:", portfolio)

    trades_df = pd.DataFrame(trades_data)
    st.write(trades_df)

    # # Plot portfolio value
    # plt.plot(p_array)
    # plt.xlabel('Trades')
    # plt.ylabel('Portfolio Value')
    # st.pyplot(plt)

# Main function to run the Streamlit app
def main():
    st.title("Trading Strategy Analysis")

    # Sidebar inputs
    st.sidebar.header("Settings")
    start_date = st.sidebar.date_input("Start Date", pd.Timestamp("2023-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.Timestamp("2024-01-01"))
    symbol = st.sidebar.text_input("Symbol", "btc-usd")
    ema_v = st.sidebar.number_input("enter ema value")
    tp = st.sidebar.number_input("enter tp value")
    sl = st.sidebar.number_input("enter sl value")

    # Download data
    df = yf.download(symbol, start=start_date, end=end_date, interval="1h")
    st.write("data")
    st.write(df)

    # Execute trading strategy
    execute_strategy(df, ema_v, tp, sl )

if __name__ == "__main__":
    main()
