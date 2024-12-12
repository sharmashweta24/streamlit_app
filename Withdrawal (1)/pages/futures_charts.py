from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

import pymongo
from datetime import datetime
client = pymongo.MongoClient("mongodb+srv://doadmin:cGeNO3YJU6149278@db-mongodb-fra1-77042-dc73fe45.mongo.ondigitalocean.com/?authSource=admin")
import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from app import login

db = client["TradingBot"]
collection = db["BackTest"]
col = db["CopyTrade"]
col1 = db["Report"]
col2 = db["Bots"]
col3 = db["BotRisk"]
col4 = db["TradeHistory"]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def make_chart(bot_id):
    data = []
    get_trade_details = col.find_one({'CopyTradeID': bot_id, 'Status': 'ACTIVE','Exchange_Type':'FUTURES'}, {'_id': 0})
    if get_trade_details is None:
        return data
    total_trades = col4.find({'CopyTradeID': bot_id}, {'_id': 0})
    for trade in total_trades:
        symbol = trade['Symbol']
        price = trade['Price']
        side = trade['Side']
        quantity = trade['Quantity']
        datetime = trade['DateTime']
        ps = trade['PositionSide']
        data.append({'Symbol': symbol, 'Price': price, 'Side': side, 'Quantity': quantity, 'Datetime': datetime, 'PositionSide': ps})
    return data


def main():
    st.title("Trade History Visualization Futures Only")
    bot_id = st.text_input("Enter Bot ID:")
    if st.button("Search"):
        if bot_id:
            trade_data = make_chart(bot_id)
            if not trade_data:
                st.warning("No active trades found for the given Bot ID Or Invalid Bot ID.")
            else:
                df = pd.DataFrame(trade_data)
                df['Datetime'] = pd.to_datetime(df['Datetime'])
                long_trades = df[df['PositionSide'] == 'LONG']
                short_trades = df[df['PositionSide'] == 'SHORT']
                symbol = df['Symbol'].iloc[0]
                st.markdown("---")
                st.markdown("### Summary")
                st.markdown(
                    f"<div style='display: flex; justify-content: space-between; font-size: 40px;'>"
                    f"<span style='color: #9467bd;'><strong>Symbol:</strong> {symbol}</span>"
                    f"<span style='color: #1f77b4;'><strong>Total Trades:</strong> {len(df)}</span>"
                    f"<span style='color: #2ca02c;'><strong>LONG Trades:</strong> {len(long_trades)}</span>"
                    f"<span style='color: #d62728;'><strong>SHORT Trades:</strong> {len(short_trades)}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                column1, column2 = st.columns(2)

                # Plot LONG trades
                with column1:
                    if not long_trades.empty:
                        st.subheader("LONG Trades")
                        fig = go.Figure()

                        # Plot Price Line
                        fig.add_trace(go.Scatter(
                            x=long_trades['Datetime'], 
                            y=long_trades['Price'], 
                            mode='lines', 
                            line=dict(color='lightgreen', width=2),
                            name='Price (LONG)'
                        ))

                        # Plot Buy Trades
                        buy_trades = long_trades[long_trades['Side'] == 'BUY']
                        fig.add_trace(go.Scatter(
                            x=buy_trades['Datetime'], 
                            y=buy_trades['Price'], 
                            mode='markers', 
                            marker=dict(size=10, color='green', symbol='triangle-up'),
                            name='Buy (LONG)',
                            text=[f"Quantity: {q}" for q in buy_trades['Quantity']]
                        ))

                        # Plot Sell Trades
                        sell_trades = long_trades[long_trades['Side'] == 'SELL']
                        fig.add_trace(go.Scatter(
                            x=sell_trades['Datetime'], 
                            y=sell_trades['Price'], 
                            mode='markers', 
                            marker=dict(size=10, color='red', symbol='triangle-down'),
                            name='Sell (LONG)',
                            text=[f"Quantity: {q}" for q in sell_trades['Quantity']]
                        ))

                        fig.update_layout(
                            title="Price Over Time (LONG)",
                            xaxis_title="Datetime",
                            yaxis_title="Price",
                            legend_title="Trade Type",
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig)
                    else:
                        st.info("No LONG trades available.")

                # Plot SHORT trades
                with column2:
                    if not short_trades.empty:
                        st.subheader("SHORT Trades")
                        fig = go.Figure()

                        # Plot Price Line
                        fig.add_trace(go.Scatter(
                            x=short_trades['Datetime'], 
                            y=short_trades['Price'], 
                            mode='lines', 
                            line=dict(color='lightblue', width=2),
                            name='Price (SHORT)'
                        ))

                        # Plot Buy Trades
                        buy_trades = short_trades[short_trades['Side'] == 'BUY']
                        fig.add_trace(go.Scatter(
                            x=buy_trades['Datetime'], 
                            y=buy_trades['Price'], 
                            mode='markers', 
                            marker=dict(size=10, color='blue', symbol='triangle-up'),
                            name='Buy (SHORT)',
                            text=[f"Quantity: {q}" for q in buy_trades['Quantity']]
                        ))

                        # Plot Sell Trades
                        sell_trades = short_trades[short_trades['Side'] == 'SELL']
                        fig.add_trace(go.Scatter(
                            x=sell_trades['Datetime'], 
                            y=sell_trades['Price'], 
                            mode='markers', 
                            marker=dict(size=10, color='orange', symbol='triangle-down'),
                            name='Sell (SHORT)',
                            text=[f"Quantity: {q}" for q in sell_trades['Quantity']]
                        ))

                        fig.update_layout(
                            title="Price Over Time (SHORT)",
                            xaxis_title="Datetime",
                            yaxis_title="Price",
                            legend_title="Trade Type",
                            hovermode="x unified"
                        )
                        st.plotly_chart(fig)
                    else:
                        st.info("No SHORT trades available.")

                # Pie chart for LONG vs SHORT trades
                col = st.columns(2)
                with col[0]:
                    st.subheader("Trade Distribution")
                    trade_counts = df['PositionSide'].value_counts()
                    pie_chart = px.pie(
                        names=trade_counts.index, 
                        values=trade_counts.values, 
                        title="Number of LONG vs SHORT Trades",
                        color_discrete_sequence=['lightgreen', 'lightblue']
                    )
                    st.plotly_chart(pie_chart)

                with col[1]:
                    st.subheader("Quantity Distribution (LONG/SHORT, BUY/SELL)")
                    # Assuming df is your DataFrame
                    df['PositionSide_Side'] = df['PositionSide'] + ' ' + df['Side']  # Combine PositionSide and Side into a single column

                    # Calculate total quantity for LONG and SHORT trades segmented by BUY and SELL
                    quantity_summary = df.groupby(['PositionSide_Side'])['Quantity'].sum().reset_index()

                    # Create a pie chart for the distribution
                    pie_chart = px.pie(
                        quantity_summary,
                        names='PositionSide_Side',  # Now we use the combined column
                        values='Quantity',
                        title="Total Quantity Distribution (LONG/SHORT, BUY/SELL)",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    st.plotly_chart(pie_chart)

if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    main()