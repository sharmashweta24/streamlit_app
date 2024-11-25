import streamlit as st
import pandas as pd
from app import *
from core.country_func import *

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def get_country_report(country):
    """Generates the country-specific report."""
    
    st.title(f"Country Report: {country}")
    
    # Fetch user details
    user_details = get_country(country)
    total_users = len(user_details)

    if total_users == 0:
        st.write(f"No users found for the country: {country}")
        return

    st.write(f"Total Users in {country}: {total_users}")

    # Rank Subscription Earnings
    st.subheader("Rank Subscription Earnings")
    rank_earnings_user, rank_earnings_admin = rank_subscription_earning(country)
    if rank_earnings_user or rank_earnings_admin:
        rank_data_user = pd.DataFrame(rank_earnings_user)
        rank_data_admin = pd.DataFrame(rank_earnings_admin)

        st.write("Rank Earnings by User:")
        if not rank_data_user.empty:
            st.table(rank_data_user)
        else:
            st.write("No rank earnings found for users.")

        st.write("Rank Earnings by Admin:")
        if not rank_data_admin.empty:
            st.table(rank_data_admin)
        else:
            st.write("No rank earnings found for admins.")
    else:
        st.write("No rank earnings found.")

    # Binary Subscription Earnings
    st.subheader("Binary Subscription Earnings")
    binary_earnings_user, binary_earnings_admin = binanry_subscription_earning(country)
    if binary_earnings_user or binary_earnings_admin:
        binary_data_user = pd.DataFrame(binary_earnings_user)
        binary_data_admin = pd.DataFrame(binary_earnings_admin)

        st.write("Binary Earnings by User:")
        if not binary_data_user.empty:
            st.table(binary_data_user)
        else:
            st.write("No binary earnings found for users.")

        st.write("Binary Earnings by Admin:")
        if not binary_data_admin.empty:
            st.table(binary_data_admin)
        else:
            st.write("No binary earnings found for admins.")
    else:
        st.write("No binary earnings found.")

    # Rank Details
    st.subheader("User Ranks")
    rank_details_user, rank_details_admin = get_rank(country)
    if rank_details_user or rank_details_admin:
        rank_data_user = pd.DataFrame(rank_details_user)
        rank_data_admin = pd.DataFrame(rank_details_admin)

        st.write("Rank Details by User:")
        if not rank_data_user.empty:
            st.table(rank_data_user)
        else:
            st.write("No rank details found for users.")

        st.write("Rank Details by Admin:")
        if not rank_data_admin.empty:
            st.table(rank_data_admin)
        else:
            st.write("No rank details found for admins.")
    else:
        st.write("No rank details found.")

    # User Deposits
    st.subheader("Deposits")
    deposit_data = user_calculate_deposits(country)

    user_deposits = pd.DataFrame.from_dict(deposit_data['user_details'], orient='index', columns=['USD_Recieved']).reset_index()
    user_deposits.rename(columns={'index': 'Username'}, inplace=True)

    admin_deposits = pd.DataFrame.from_dict(deposit_data['admin_details'], orient='index', columns=['USD_Recieved']).reset_index()
    admin_deposits.rename(columns={'index': 'Username'}, inplace=True)

    st.write("User Deposits:")
    if not user_deposits.empty:
        st.write(f"Total User Deposit Amount: {deposit_data['total_by_user']}")
        st.table(user_deposits)
    else:
        st.write("No user deposits found.")

    st.write("Admin Deposits:")
    if not admin_deposits.empty:
        st.write(f"Total Admin Deposit Amount: {deposit_data['total_by_admin']}")
        st.table(admin_deposits)
    else:
        st.write("No admin deposits found.")

if st.session_state.logged_in == False:
    login(st, 'Adminname', 'Password')
else:
    st.title("Country Reports Dashboard")
    country_options = user_details.distinct('Country')
    if not country_options:
        st.write("No country data available.")
    else:
        selected_country = st.selectbox("Select a country", options=country_options)
        if selected_country:
            get_country_report(selected_country)

