
import pymongo
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

from app import login,st,logout

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

def main():
    end_date = st.date_input("Select End Date")
    end_date = datetime.combine(end_date, datetime.min.time())
    if st.button("Process"):
        if end_date:
            data = list(col1.find({"DateTime": {"$gt": end_date}},{"_id": 0, 'Username': 1}))
            usernames = [i['Username'] for i in data]
            usernames = list(set(usernames))
            st.markdown(f"<h3 style='color: green;'>Total Users:{len(usernames)}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='color: red;'>This may take some time depending on number of users</h3>", unsafe_allow_html=True)
            my_bar = st.progress(0, text="Processing...")
            progress_lock = threading.Lock()
            progress = 0
            total_users = len(usernames)
            def process_user(i):
                nonlocal progress
                i = i.lower()
                st.markdown(f"<h3 style='color: green;'>Processing User:{i}</h3>", unsafe_allow_html=True)
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
                    if x.get('Package_Type') == "BOT":
                        if x.get('Executed_By') == 'Admin':
                            total_bot_admin += float(x.get('Price', 0))  
                            total_package_admin += float(x.get('Price', 0))
                        else:
                            total_bot_user += float(x.get('Price', 0))
                            total_package_user += float(x.get('Price', 0))
                    else:
                        if x.get('Executed_By') == 'Admin': 
                            total_trade_admin += float(x.get('Price', 0))  
                            total_package_admin += float(x.get('Price', 0))
                            roi_check.append(x.get('ROI_Withdrawable', False))
                            roi_dist.append(x.get('ROI_Distribution', False))
                        else:
                            total_trade_user += float(x.get('Price', 0))
                            total_package_user += float(x.get('Price', 0))

                dd['Total of Package By User'] = total_package_user
                dd['Sum of TP package By User'] = total_trade_user
                dd['Sum of Bot package By User'] = total_bot_user
                dd['Total of Package By Admin'] = total_package_admin
                dd['Sum of TP package By Admin'] = total_trade_admin
                dd['Sum of Bot package By Admin'] = total_bot_admin
                dd['ROI_Withdrawable'] = any(roi_check) if roi_check else False
                dd['ROI_Distribution'] = any(roi_dist) if roi_check else False
                network = col4.find_one({'Username': i}, {'_id': 0, 'Username': 0})
                total_deposit_team = 0
                # Process conditions
                conditions = col6.find_one({'Username': i}, {'_id': 0})
                if conditions:
                    dd['ROI Balance Withdrawable'] = conditions['Transfer_from']['ROI_Balance']

                sub1 = col3.find_one({'Username': i, 'Package_Type': "TRADE",'Status': True}, {'_id': 0})
                if sub1:
                    dd['Date of First Subscription'] = sub1['DateTime'].strftime('%Y-%m-%d %H:%M:%S') if sub1['DateTime'] else None

                # Process withdrawal
                withdrawal = col1.find({'Username': i,'Status': 'APPROVED'}, {'_id': 0})
                total_withdrawal = 0

                for w in withdrawal:
                    total_withdrawal += float(w['Amount'])
                dd['Total Withdrawal'] = total_withdrawal

                # Process analytics
                analytics = col8.find_one({'Username': i}, {'_id': 0})
                if analytics:
                    dd['LifeTime Bianary Left Side'] = analytics['User_Binary_Business_0']
                    dd['LifeTime Bianary Right Side'] = analytics['User_Binary_Business_1']
                    dd['User Team Bussiness'] = analytics['User_Team_Business']
                    
                direct  = 0
                if network:
                    count = 1
                    # print('Inside network')
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
                dd['Direct Bussiness'] = direct
                dd['Team Deposit by user Coinpayment '] = total_deposit_team

                dd['5X By Direct Bussiness'] = True if (dd['Total of Package By Admin']*5) <= dd['Direct Bussiness'] else False 
                dd['5X By NetWork Bussiness'] = True if (dd['Total of Package By Admin']*5) <= (dd['LifeTime Bianary Left Side'] + dd['LifeTime Bianary Right Side']) else False 

                return dd
            
            with st.spinner("Processing..."):  
                with ThreadPoolExecutor(max_workers=50) as executor:
                    results = list(executor.map(process_user, usernames))
            for _ in range(progress):
                my_bar.progress(progress / total_users, text=f"Processing {_+1}/{total_users}")
            

            df = pd.DataFrame(results)
            if df.empty:
                st.error("No data found for the selected date.")
                return
            csv_filename = datetime.now().strftime("%Y-%m-%d %H-%M-%S")+" withdrawl_performance.csv"
            st.download_button(
                label="Download CSV",
                data=df.to_csv(index=False),
                file_name=csv_filename,
                mime="text/csv"
            )
            st.success(f"CSV file '{csv_filename}' generated successfully.")
            st.balloons()
    else:
        st.warning("Please enter a CSV filename to enable the 'Generate CSV' button.")


if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    main()