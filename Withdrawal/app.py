from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

import streamlit as st
from core.functions import *

st.set_page_config(layout="wide", page_title="Odecent", page_icon="👤")

def welcome_page(st):
    st.title("Welcome to Odecent Admin Panel")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    welcome_page(st)




