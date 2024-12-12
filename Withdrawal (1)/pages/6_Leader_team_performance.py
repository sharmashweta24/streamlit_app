import pymongo
import streamlit as st
import pandas as pd
from app import login
from concurrent.futures import ThreadPoolExecutor
from core.user_func import get_user_network
import io


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

def process_user(i):
    i = i.lower()
    dd = {} 
    dd['Username'] = i
    name = col5.find_one({'Username': i}, {'_id': 0})
    dd['Name'] = name['Name'] 
    dd['Country'] = name['Country']
    sub = col3.find({'Username': i,'Status': True}, {'_id': 0})
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
    dd['Sum of TP package By User'] = total_trade_user
    dd['Sum of TP package By Admin'] = total_trade_admin
    dd['Sum of Bot package By User'] = total_bot_user
    dd['Sum of Bot package By Admin'] = total_bot_admin
    dd['Total of Package By User'] = total_package_user
    dd['Total of Package By Admin'] = total_package_admin
    dd['ROI_Distribution'] = any(roi_dist) if roi_check else False
    dd['ROI_Withdrawable'] = any(roi_check) if roi_check else False


    
    network = col4.find_one({'Username': i}, {'_id': 0, 'Username': 0})
    total_deposit_team = 0
    conditions = col6.find_one({'Username': i}, {'_id': 0})
    if conditions:
        dd['ROI Balance Withdrawable'] = conditions['Transfer_from']['ROI_Balance']

    sub1 = col3.find_one({'Username': i, 'Package_Type': "TRADE",'Status': True}, {'_id': 0})
    if sub1:
        dd['Date of First Subscription'] = sub1['DateTime'].strftime('%Y-%m-%d %H:%M:%S') if sub1['DateTime'] else None

    withdrawal = col1.find({'Username': i,'Status': 'APPROVED'}, {'_id': 0})
    total_withdrawal = 0

    for w in withdrawal:
        total_withdrawal += float(w['Amount'])

    analytics = col8.find_one({'Username': i}, {'_id': 0})
    if analytics:
        dd['LifeTime Bianary Left Side'] = analytics['User_Binary_Business_0']
        dd['LifeTime Bianary Right Side'] = analytics['User_Binary_Business_1']
        dd['User Team Bussiness'] = analytics['User_Team_Business']
        
    direct  = 0
    if network:
        count = 1
        while count <= len(network):
            for j in network[str(count)]:
                cc = col2.find({'Username': j, 'Status': 'SUCCESS'}, {'_id': 0})
                for rr in cc:
                    if rr.get('By') == 'User': 
                        total_deposit_team += float(rr.get('USD_Recieved', 0)) 
                if count == 1:
                    aaaa = col3.find({'Username': j, 'Status': True,'Executed_By':'User'}, {'_id': 0})
                    for aaa in aaaa:
                        direct += float(aaa.get('Price', 0))
            count += 1
    dd['Team Deposit by user Coinpayment '] = total_deposit_team
    dd['Direct Bussiness'] = direct

    dd['Total Withdrawal'] = total_withdrawal

    dd['5X By Direct Bussiness'] = True if (total_package_admin*5) <= dd['Direct Bussiness'] else False 
    dd['5X By NetWork Bussiness'] = True if (total_package_admin*5) <=((dd['LifeTime Bianary Left Side'] + dd['LifeTime Bianary Right Side'])) else False 

    return dd

def main():
    st.title('Search User Data and Download')
    username_search = st.text_input('Enter Username to Search:')
    usernames = get_user_network(username_search)
    usernames.append(username_search)

    if st.button('Search') and username_search:
        total_users = len(usernames)
        progress_bar = st.progress(0)  
        progress_status = st.empty()  

        with st.spinner("Processing..."):
            results = []  

            with ThreadPoolExecutor(max_workers=50) as executor:
                for i, result in enumerate(executor.map(process_user, usernames), start=1):
                    results.append(result)
                    progress = i / total_users
                    progress_bar.progress(progress)
                    progress_status.text(f"Processing {i}/{total_users} users...")

        # Create CSV data
        csv_data = pd.DataFrame(results)
        st.download_button(
            label="Download CSV",
            data=csv_data.to_csv(index=False),
            file_name=f"{username_search} data with team.csv",
            mime="text/csv"
        )
        st.balloons()


if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    main()