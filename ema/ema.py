import datetime
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def get_data(symbol, start_date, end_date):
    df = yf.download(symbol, start_date, end_date, interval="1h")
    return df

def simulate_trades(data, trade_dir, ema, take_profit, stop_loss):
    df = data
    position_type = "na"
    status = "not in trade"

    tp = take_profit/100  # 1%
    sl = stop_loss/100  # 5%
    new_short_tp = take_profit/100
    new_short_sl = stop_loss/100

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
            if trade_dir == "long":
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
                
            elif trade_dir == "short":
            # Condition for short trades
                if (
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
            
            elif trade_dir == "both":
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
            if trade_dir == "long":
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

            elif trade_dir == "short":
                # Short TP and SL
                if position_type == "Short trade":
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

            elif trade_dir == "both":
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
                if position_type == "Short trade":
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
    trades_df = pd.DataFrame(trades_data)
    trades_df.set_index("Date", inplace=True)
    num_trades = len(trades_df)
    num_trades_hit_tp = trades_df['Reason'].eq('long_tp_hit').sum() + trades_df['Reason'].eq('short_tp_hit').sum()
    num_trades_hit_sl = trades_df['Reason'].eq('long_sl_hit').sum() + trades_df['Reason'].eq('short_sl_hit').sum()
    num_trades_exit_without_tp_sl = trades_df['Reason'].eq('third_condition').sum()
    portfolio_value = trades_df['Portfolio Value'].iloc[-1]
    pnl_ratio = (num_trades_hit_tp / num_trades) * 100 if num_trades > 0 else 0

    trade_stats = {
        'num_trades': num_trades,
        'num_trades_hit_tp': num_trades_hit_tp,
        'num_trades_hit_sl': num_trades_hit_sl,
        'num_trades_exit_without_tp_sl': num_trades_exit_without_tp_sl,
        'portfolio_value': portfolio_value,
        'pnl_ratio': pnl_ratio
    }
    return trade_stats, trades_data

def main():
    st.title("Trading Strategy Analyzer")

    # Sidebar inputs
    start_date = st.sidebar.date_input("Start Date", datetime.date(2023, 1, 1))
    end_date = st.sidebar.date_input("End Date")
    symbol = st.sidebar.text_input("Symbol", value="BTC-USD")
    trade_dir = st.sidebar.selectbox("Trade Direction", ["long", "short", "both"])
    ema = st.sidebar.number_input("EMA", value=200)
    take_profit = st.sidebar.slider("Take Profit (%)", 1, 10, 5)
    stop_loss = st.sidebar.slider("Stop Loss (%)", 1, 10, 5)

    # Get data
    data = get_data(symbol, start_date, end_date)

    # Simulate trades
    trade_stats, trades_df = simulate_trades(data, trade_dir, ema, take_profit, stop_loss)

    # Display trade statistics
    st.subheader("Trade Statistics")
    st.write("Number of trades executed:", trade_stats['num_trades'])
    st.write("Number of trades exited by hitting TP:", trade_stats['num_trades_hit_tp'])
    st.write("Number of trades exited by hitting SL:", trade_stats['num_trades_hit_sl'])
    st.write("Exit without TP or SL:", trade_stats['num_trades_exit_without_tp_sl'])
    st.write("Portfolio Value:", trade_stats['portfolio_value'])
    st.write("PnL ratio:", trade_stats['pnl_ratio'])

    # Display trades DataFrame
    st.subheader("Trades DataFrame")
    st.table(trades_df)

if __name__ == "__main__":
    main()
