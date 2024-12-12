import pymongo
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from app import login, st, logout

client = pymongo.MongoClient("mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin")  
db = client['Odecent_B']

col1 = db['Withdrawal_Request'] 
col2 = db['Deposit_Transaction']
col3 = db['Subscription_Qualification']
col4 = db['User_Network']
col5 = db['User_Details']
col6 = db['User_Conditions']
col7 = db['User_Wallet']
col8 = db['User_Analytics']

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def fetch_network_users(username, network_set):
    """
    Recursively fetch all users in the network.
    """
    if username in network_set: 
        return network_set
    
    network_set.add(username)

    network = col4.find_one({'Username': username}, {'_id': 0, 'Username': 0})
    if network:
        for level in network.values():
            for sub_user in level:
                fetch_network_users(sub_user, network_set)
    return network_set

def process_user(i):
    """
    Process the data for a single user and return a dictionary of their details.
    """
    dd = {}
    i = i.lower()
    dd['Username'] = i
    name = col5.find_one({'Username': i}, {'_id': 0})
    dd['Name'] = name['Name'] if name else None
    dd['Country'] = name['Country'] if name else None
    
    sub = col3.find({'Username': i, 'Status': True}, {'_id': 0})
    sub = list(sub)
    
    total_trade_admin = 0
    total_bot_admin = 0
    total_bot_user = 0
    total_trade_user = 0
    total_package_user = 0
    total_package_admin = 0
    roi_check = []
    roi_dist = []
    
    for x in sub:
        if x.get('Package_Type') == "BOT" and x.get('Executed_By') == 'Admin':
            total_bot_admin += float(x.get('Price', 0))
            total_package_admin += float(x.get('Price', 0))
        else:
            if x.get('Executed_By') == 'Admin': 
                total_trade_admin += float(x.get('Price', 0))
                total_package_admin += float(x.get('Price', 0))
                roi_check.append(x.get('ROI_Withdrawable', False))
                roi_dist.append(x.get('ROI_Distribution', False))
        if x.get('Executed_By') == 'User' and x.get('Package_Type') == 'BOT':
            total_bot_user += float(x.get('Price', 0))
            total_package_user += float(x.get('Price', 0))
        else:
            if x.get('Executed_By') == 'User':
                total_trade_user += float(x.get('Price', 0))
                total_package_user += float(x.get('Price', 0))

    dd['Total of Package By User'] = total_package_user
    dd['Total of Package By Admin'] = total_package_admin
    dd['Sum of TP package By User'] = total_trade_user
    dd['Sum of Bot package By User'] = total_bot_user
    dd['Sum of TP package By Admin'] = total_trade_admin
    dd['Sum of Bot package By Admin'] = total_bot_admin
    dd['ROI_Withdrawable'] = any(roi_check) if roi_check else False
    dd['ROI_Distribution'] = any(roi_dist) if roi_dist else False

    conditions = col6.find_one({'Username': i}, {'_id': 0})
    if conditions:
        dd['ROI Balance Withdrawable'] = conditions['Transfer_from']['ROI_Balance']

    sub1 = col3.find_one({'Username': i, 'Package_Type': "TRADE", 'Status': True}, {'_id': 0})
    if sub1:
        dd['Date of First Subscription'] = sub1['DateTime'].strftime('%Y-%m-%d %H:%M:%S') if sub1['DateTime'] else None

    withdrawal = col1.find({'Username': i, 'Status': 'APPROVED'}, {'_id': 0})
    total_withdrawal = sum(float(w['Amount']) for w in withdrawal)
    dd['Total Withdrawal'] = total_withdrawal

    analytics = col8.find_one({'Username': i}, {'_id': 0})
    if analytics:
        dd['LifeTime Bianary Left Side'] = analytics.get('User_Binary_Business_0', 0)
        dd['LifeTime Bianary Right Side'] = analytics.get('User_Binary_Business_1', 0)
        dd['User Team Bussiness'] = analytics.get('User_Team_Business', 0)
    
    return dd

def main():
    user = st.text_input("Enter a Leader Name:")
    if st.button("Process"):
        if user:
            st.markdown("<h3 style='color: red;'>Fetching user network...</h3>", unsafe_allow_html=True)
            
            network_set = fetch_network_users(user, set())
            usernames = list(network_set)
            
            st.markdown(f"<h3 style='color: green;'>Total Users in Network: {len(usernames)}</h3>", unsafe_allow_html=True)
            
            my_bar = st.progress(0, text="Processing...")
            progress_lock = threading.Lock()
            progress = 0
            total_users = len(usernames)
            
            def update_progress():
                nonlocal progress
                with progress_lock:
                    progress += 1
                    my_bar.progress(progress / total_users, text=f"Processing {progress}/{total_users}")

            with st.spinner("Processing network users..."):
                with ThreadPoolExecutor(max_workers=50) as executor:
                    results = []
                    for user_data in executor.map(process_user, usernames):
                        results.append(user_data)
                        update_progress()

            df = pd.DataFrame(results)
            csv_filename = f"{user}_network_performance.csv"
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name=csv_filename,
                mime="text/csv"
            )
            st.success(f"CSV file '{csv_filename}' generated successfully.")
            st.balloons()
        else:
            st.warning("Please enter a username to process.")

if st.session_state.logged_in == False:
    login(st, 'Adminname', 'Password')
else:
    main()
