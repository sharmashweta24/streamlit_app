import streamlit as st
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

# MONGODB_URL = 'mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/'
# DATABASE_NAME = 'OdecenstTestClone'

MONGODB_URL = "mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin"
DATABASE_NAME = 'Odecent_B' 
def connect_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

db = connect_database()

async def fetch_binary(username, username2):
    binary_collection = db['Binary_Location']
    settings_collection = db['Settings']

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

    max_level = settings['Binary_Level']
    if max_level == 0:
        return {"msg": "Binary Level is greater than 200"}, 305

    user_analytics = []

    while len(loc) > 0:
        user = await binary_collection.find_one(
            {'Location': loc},
            {'_id': 0, 'Username': 1}
        )
        if user:
            binary_level = len(loc) - 1
            user_analytics.append({
                'Username': user.get('Username'),
                'Binary Level': binary_level,
                'Location': loc
            })
        loc = loc[:-1] 
        if user and user['Username'] == username2:
            break

    if any(user['Username'] == username2 for user in user_analytics):
        return user_analytics, 200
    else:
        return {'msg': "Please check username"}, 305

def login():
    st.title("Login to Dashboard")
    
    username = st.text_input("Adminname:")
    password = st.text_input("Password:", type="password")
    
    predefined_username = "admin" 
    predefined_password = "vWDhLeGIPUdmUJnTxDXjRvxrj" 

    if st.button("Login"):
        if username == predefined_username and password == predefined_password:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

def dashboard():
    st.title("Binary Location Tracker Dashboard")
    st.markdown("<p style='color:red;'>To get the location of a user, enter the username of the leader and the username of the admin.</p>", unsafe_allow_html=True)

    
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in first.")
        login()
        return

    username = st.text_input("Enter Username from(Leader):")
    username2 = st.text_input("Enter Username to(admin):")

    if st.button("Fetch Data"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        progress = st.progress(0)
        progress_text = st.empty()
        progress_text.text("Progress: 0/100")

        progress.progress(20)
        progress_text.text("Progress: 20/100")

        data, status = loop.run_until_complete(fetch_binary(username, username2))

        progress.progress(70)
        progress_text.text("Progress: 70/100")

        if status == 200:
            progress.progress(100)
            progress_text.text("Progress: 100/100")

            st.write(f"**Sponsor Location:** {data[0]['Location']}")
            st.write(f"**Users in Binary Tree:** {len(data)}")
            st.write("**User Data:")
            st.table(data[::-1])
        else:
            progress.progress(100)
            progress_text.text("Progress: 100/100")
            st.error(data['msg'])

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard()
else:
    login()
