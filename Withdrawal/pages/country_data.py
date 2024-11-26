import streamlit as st
import pandas as pd
from app import *
from core.country_wise import *

# Ensure session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def create_dataframe(data, role):
    df = pd.DataFrame([
        {"Package_Type": k, "Price": v[role]} 
        for k, v in data.items() if v[role] > 0
    ])
    df["Package_Type"] = df["Package_Type"].astype(str)
    df["Price"] = pd.to_numeric(df["Price"], errors='coerce')
    df = df.dropna(subset=["Price"])
    
    return df

def display_country_user_counts():
    """Displays the number of users in each country."""
    try:
        country_counts = country_total()

        if not country_counts:
            st.write("No countries found.")
        else:
            st.title("User Count by Country")
            # for i, j in country_counts.items():
            #     st.markdown(f'**{i}:** {j}')
            counter = 0
            max_in_row = 5
            row = "<div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>"

            for i, j in country_counts.items():
                row += f"<div style='flex: 1 1 18%; margin: 10px 0; padding: 5px; text-align: center;'><strong>{i} : </strong> {j}</div>"
                counter += 1
                if counter == max_in_row:
                    row += "</div><div style='display: flex; flex-wrap: wrap; justify-content: space-between;'>"
                    counter = 0
            if row:
                row += "</div>"

            st.markdown(row, unsafe_allow_html=True)

            # country_df = pd.DataFrame(list(country_counts.items()), columns=['Country', 'User Count'])

            # st.table(country_df)
    except Exception as e:
        st.error(f"An error occurred while fetching country data: {e}")

def get_country_report(country):
    st.title(f"Country Report: {country}")
    by_user_data, by_admin_data = country_wise(country)
    total_users = len(by_user_data) + len(by_admin_data)
    if total_users == 0:
        st.write(f"No users found for the country: {country}")
        return
    st.write(f"Total Users in {country}: {total_users}")

    # Rank Details
    st.markdown("<h3 style='color: yellow;'>User Ranks</h3>", unsafe_allow_html=True)
    rank_details = get_rank(country)
    if rank_details:
        rank_data = pd.DataFrame(list(rank_details.items()), columns=["Rank", "Count"])
        st.markdown("<h4 style='font-size: 20px;'>Rank Details:</h4>", unsafe_allow_html=True)
        st.table(rank_data)
    else:
        st.write("No rank details found.")

    # Subscription Data
    st.markdown("<h3 style='color: yellow;'>Subscription Data (TRADE & BOT)</h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='color: lightgreen; font-size: 20px;'>Trade Subscription Details</h4>", unsafe_allow_html=True)
    trade_data, bot_data = get_subscription(country)

    if trade_data:
        col1, col2 = st.columns(2)

        with col1:
            trade_user_data = pd.DataFrame([
                {"Package_Type": k, "Price": v['by_user']} 
                for k, v in trade_data.items() if v['by_user'] > 0
            ])
            st.markdown("<h5 style='font-size: 18px;'>Trade Subscriptions by User:</h5>", unsafe_allow_html=True)
            st.table(trade_user_data)

        with col2:
            trade_admin_data = pd.DataFrame([
                {"Package_Type": k, "Price": v['by_admin']} 
                for k, v in trade_data.items() if v['by_admin'] > 0
            ])
            st.markdown("<h5 style='font-size: 18px;'>Trade Subscriptions by Admin:</h5>", unsafe_allow_html=True)
            st.table(trade_admin_data)
    else:
        st.write("No trade subscriptions found.")

    if bot_data:
        st.markdown("<h4 style='color: lightcoral; font-size: 20px;'>Bot Subscription Details</h4>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            bot_user_data = pd.DataFrame([
                {"Package_Type": k, "Price": v['by_user']} 
                for k, v in bot_data.items() if v['by_user'] > 0
            ])
            st.markdown("<h5 style='font-size: 18px;'>Bot Subscriptions by User:</h5>", unsafe_allow_html=True)
            st.table(bot_user_data)

        with col2:
            bot_admin_data = pd.DataFrame([
                {"Package_Type": k, "Price": v['by_admin']} 
                for k, v in bot_data.items() if v['by_admin'] > 0
            ])
            st.markdown("<h5 style='font-size: 18px;'>Bot Subscriptions by Admin:</h5>", unsafe_allow_html=True)
            st.table(bot_admin_data)
    else:
        st.write("No bot subscriptions found.")


    # Deposits
    st.markdown("<h3 style='color: yellow;'>Deposits</h3>", unsafe_allow_html=True)
    deposit_data = user_calculate_deposits(country)

    user_deposits = pd.DataFrame.from_dict(deposit_data['user_details'], orient='index', columns=['USD_Recieved']).reset_index()
    user_deposits.rename(columns={'index': 'Username'}, inplace=True)

    admin_deposits = pd.DataFrame.from_dict(deposit_data['admin_details'], orient='index', columns=['USD_Recieved']).reset_index()
    admin_deposits.rename(columns={'index': 'Username'}, inplace=True)


    st.markdown(f"<h4 style='font-size: 20px;'>Total Deposits: {deposit_data['total_user']+deposit_data['total_admin']}</h4>",unsafe_allow_html=True)

    st.markdown("<h4 style='font-size: 20px;'>Coin Payments Deposits:</h4>", unsafe_allow_html=True)
    if not user_deposits.empty:
        st.write(f"Total Coin Payments Deposits Amount: {deposit_data['total_user']}")
        st.table(user_deposits)
    else:
        st.write("No CoinPayments deposits found.")

    st.markdown("<h4 style='font-size: 20px;'>Admin Deposits:</h4>", unsafe_allow_html=True)
    if not admin_deposits.empty:
        st.write(f"Total Admin Deposit Amount: {deposit_data['total_admin']}")
        st.table(admin_deposits)
    else:
        st.write("No admin deposits found.")

    # Withdrawal Data
    st.markdown("<h3 style='color: yellow;'>Withdrawal</h3>", unsafe_allow_html=True)
    withdrawal_data = get_withdrawal_details(country)
    st.table(withdrawal_data)


if st.session_state.logged_in == False:
    login(st, 'Adminname', 'Password')
else:
    display_country_user_counts()
    country_options = user_details.distinct('Country')
    if not country_options:
        st.write("No country data available.")
    else:
        selected_country = st.selectbox("Select a country", options=country_options)
        if selected_country:
            get_country_report(selected_country)
