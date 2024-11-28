from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from app import *
from core.fund_flow import *
from core.reward import *
import pandas as pd
import streamlit as st
from datetime import datetime

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def money_flow_page():
    
    st.title("Money Flow Details")
    
    username = st.text_input("Enter username to search for fund flow details", "")

    if username:
        rewards_find = rewards(username)
    else:
        rewards_find = {'Binary_Reward': [], 'Weekly_Reward': [], 'Compound_Reward': [], 'Rank_Reward': []}

    reward_type = st.selectbox(
        "Select Reward Type",
        options=list(rewards_find.keys())
    )

    if reward_type:
        st.subheader(f"{reward_type} Details")
        reward_data = rewards_find[reward_type]

        if reward_data:
            all_data = []
            for entry in reward_data:
                all_data.append(entry)
            
            df = pd.DataFrame(all_data)
            
            st.table(df)
        else:
            st.write("No data available for this reward type.")



    if username.strip(): 
        user_fund_details = fund_flow_details(username)
        user_subscription_details = user_subscription(username)

        if not user_fund_details and not user_subscription_details:
            st.error(f"No data found for username: {username}")
            return
        st.markdown("<h2 style='color: orange;'>Fund Flow Details</h2>", unsafe_allow_html=True)
        if user_fund_details:
            fund_flow_table = pd.DataFrame(user_fund_details)
            st.table(fund_flow_table)
        else:
            st.info("No Fund Flow Details available.")

        st.markdown("<h2 style='color: orange;'>Subscription Details</h2>", unsafe_allow_html=True)
        if user_subscription_details:
            subscription_table = pd.DataFrame(user_subscription_details)
            st.table(subscription_table)
        else:
            st.info("No Subscription Details available.")
            
        st.markdown("<h2 style='color: orange;'>Money Transactions</h2>", unsafe_allow_html=True)
        user_money_transactions = user_money_flow(username).get('Money_Transactions', [])
        if user_money_transactions:
            transaction_table = pd.DataFrame(user_money_transactions)
            st.table(transaction_table)
        
        all_user_info = all_user_details(username)

        for user, details in all_user_info.items():
                st.markdown(f"<h2 style='color: orange;'>Details for {user}</h2>", unsafe_allow_html=True)
                
                st.markdown("<h3>Fund Flow</h3>", unsafe_allow_html=True)
                if details["Fund_Flow"]:
                    fund_flow_table = pd.DataFrame(details["Fund_Flow"])
                    st.table(fund_flow_table)
                else:
                    st.write("No fund flow records found.")
                
                st.markdown("<h3>Subscription</h3>", unsafe_allow_html=True)
                if details["Subscription"]:
                    subscription_table = pd.DataFrame(details["Subscription"])
                    st.table(subscription_table)
                else:
                    st.write("No subscription records found.")
                
                st.markdown("<h3>Money Transactions</h3>", unsafe_allow_html=True)
                if details["Money_Transactions"]:
                    transaction_table = pd.DataFrame(details["Money_Transactions"])
                    st.table(transaction_table)
                else:
                    st.write("No money transactions found.")


if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    money_flow_page()
