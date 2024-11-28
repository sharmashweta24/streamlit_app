import streamlit as st
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import pandas as pd

MONGODB_URL = 'mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/'
DATABASE_NAME = 'OdecenstTestClone'

def connect_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

db = connect_database()

async def fetch_admin_data(username2):
    analytics_collection = db['User_Analytics']
    admin = await analytics_collection.find_one(
        {'Username': username2},
        {
            '_id': 0,
            'Total_Direct': 1,
            'Total_Team': 1,
            'Rank_Business': 1,
            'Binary_Business': 1
        }
    )
    return admin or {}

async def fetch_binary(username, username2):
    binary_collection = db['Binary_Location']
    settings_collection = db['Settings']
    analytics_collection = db['User_Analytics']
    
    sponsor = await binary_collection.find_one(
        {'Username': username},
        {'_id': 0, 'Location': 1}
    )
    
    if not sponsor:
        return {'msg': f"User {username} is invalid"}, 305

    loc = sponsor['Location']
    settings = await settings_collection.find_one({}, {'_id': 0, 'Binary_Level': 1})

    if not settings:
        return {'msg': "Binary_Level setting not found"}, 305

    count = settings['Binary_Level']
    user_analytic = await analytics_collection.find_one(
        {'Username': username},
        {
            '_id': 0,
            'Total_Direct': 1,
            'Total_Team': 1,
            'Rank_Business': 1,
            'Binary_Business': 1
        }
    )

    user_analytics = []   
    user_location_chain = []  
    while len(loc) > 1 and count > 0:
        user = await binary_collection.find_one(
            {'Location': loc[:-1]},
            {'_id': 0, 'Username': 1, 'Location': 1}
        )

        if user:
            user_analytics.append(user.get('Username')) 
            user_location_chain.append({
                'Username': user.get('Username'),
                'Location': loc[:-1]  
            })
        
        loc = loc[:-1] 
        count -= 1
        if user['Username'] == username2:
            break

    if len(user_location_chain) == 0 or user_location_chain[-1]['Username'] != username2:
        user_location_chain.append({'Username': username2, 'Location': '0'})  # Admin location is '0'

    if username2 in user_analytics:
        return user_analytic, 200, sponsor, user_location_chain
    else:
        return {'msg': "Please check username"}, 305, sponsor, user_location_chain

async def main(username, username2):
    data, status, sponsor, user_location_chain = await fetch_binary(username, username2)
    if status == 200:
        admin_data = await fetch_admin_data(username2)
        difference_data = {
            key: admin_data.get(key, 0) - data.get(key, 0)
            for key in data
        }
        sponsor_df = pd.DataFrame([{
            'Username': sponsor.get('Username', ''),
            'Location': sponsor.get('Location', '')
        }])

        location_chain_df = pd.DataFrame(user_location_chain)

        user_df = pd.DataFrame([data])
        admin_df = pd.DataFrame([admin_data])
        diff_df = pd.DataFrame([difference_data])

        st.subheader('Sponsor Information')
        st.write(sponsor_df)

        st.subheader('Sponsor Location Chain')
        st.table(location_chain_df)

        st.subheader('User Analytics Data')
        st.table(user_df)

        st.subheader('Admin Analytics Data')
        st.table(admin_df)

        st.subheader('Difference Data')
        st.table(diff_df)
    
    elif status == 305:
        st.error(data['msg'])

# Login functionality
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Login to Access the Application")
    username_input = st.text_input("Enter Username")
    password_input = st.text_input("Enter Password", type="password")
    
    correct_username = "admin"
    correct_password = "vWDhLeGIPUdmUJnTxDXjRvxrj"
    
    if st.button("Login"):
        if username_input == correct_username and password_input == correct_password:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password. Please try again.")
else:
    st.title("User and Admin Analytics")
    
    username = st.text_input("Enter Username")
    username2 = st.text_input("Enter Admin Username")
    
    if st.button("Fetch Data"):
        if username and username2:
            asyncio.run(main(username, username2))
        else:
            st.warning("Please enter both usernames.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.success("Logged out successfully.")
