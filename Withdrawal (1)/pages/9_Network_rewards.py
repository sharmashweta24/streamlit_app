from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
import streamlit as st
from datetime import datetime
import pandas as pd
from core.network_reward_fun import *
from app import login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def process_record():
    st.title("Network(Binary) Transactions Processor")

    if not st.session_state.get("logged_in", False):
        st.subheader("Please log in to continue.")
        return

    start_date = st.date_input("Select From Date")
    end_date = st.date_input("Select To Date")

    if st.button("Process Network(Binary) Transactions"):
        if not start_date or not end_date:
            st.error("Please select both a start date and an end date.")
        elif start_date > end_date:
            st.error("Start date cannot be after the end date.")
        else:
            with st.spinner("Processing transactions..."):
                transactions = fetch_transactions(start_date, end_date)  
                results = process_transactions(transactions)
                df = pd.DataFrame(results)

                if df.empty:
                    st.error("No transactions found for the selected date range.")
                    return

            csv_filename = datetime.now().strftime("%Y-%m-%d %H-%M-%S")+" network_rewards.csv"
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name=csv_filename,
                mime="text/csv",
            )
            st.success(f"CSV file '{csv_filename}' generated successfully.")
            st.balloons()
    else:
        st.subheader("Please log in to continue")
    
if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    process_record()
