

from os.path import abspath, join, dirname
from sys import path
import streamlit as st
import asyncio
from core.binary_function import main  
from app import *

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def fetch_and_display_data(username, username2):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    data, status = loop.run_until_complete(main(username, username2))

    if status == 200:
        st.write(f"**Sponsor Location:** {data[0]['Location']}")
        st.write(f"**Users in Binary Tree:** {len(data)}")
        st.write("**User Data:**")
        st.table(data)
    else:
        st.error(data['msg'])

st.title("Binary Location Tracker")


if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    username = st.text_input("Enter Sponsor Username:")
    username2 = st.text_input("Enter Target Username:")
    if st.button("Fetch Data"):
        fetch_and_display_data(username, username2)


