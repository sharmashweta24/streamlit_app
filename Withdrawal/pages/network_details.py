from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from app import *
from core.user_func import *
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def user_network():
    if st.button("Logout"):
        logout(st)
    st.markdown("<h4 style='color:white'>Odecent User Network Details</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:red'>Don't refresh page after login, it will logout you</h3>", unsafe_allow_html=True)
    username = st.text_input("Username")
    if st.button("Search"):
        if username == '':
            st.error("Please enter username")
            return
        else:
            user_details = get_user_details(username)
            if user_details is None:
                st.error("User not found")
                return
            else:
                cols = st.columns(3)
                for i, (key, value) in enumerate(user_details.items()):
                    col = cols[i % 3] 
                    col.markdown(f"<h5>{key}: {value}</h5>", unsafe_allow_html=True)
                user_deposite_user, user_deposite_admin = get_user_deposite(username=username)
                cols = st.columns(3)
                for i, (key, value) in enumerate([("Deposite By User ", user_deposite_user), ("Deposite By Admin", user_deposite_admin)]):
                    col = cols[i % 3] 
                    col.markdown(f"<h5 style='color: green;'>{key}: {value}</h5>", unsafe_allow_html=True)
                user_trade_deatails,user_bot_deatils,user_trade_by_user,user_trade_by_admin,user_bot_user,user_bot_admin = get_user_sub(username)
                st.markdown("<h3 style='color: yellow;'>User Subscription</h3>", unsafe_allow_html=True)
                st.table(user_trade_deatails+user_bot_deatils)
                cols = st.columns(2)
                st.markdown("<h4 style='color: yellow;'>By User</h4>", unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("<h8 style='color: yellow;'>Trade</h8>", unsafe_allow_html=True)
                    st.table(user_trade_by_user)
                with cols[1]:
                    st.markdown("<h8 style='color: yellow;'>Bot</h8>", unsafe_allow_html=True)
                    st.table(user_bot_user)
                st.markdown("<h4 style='color: yellow;'>By Admin</h4>", unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("<h8 style='color: yellow;'>Trade</h8>", unsafe_allow_html=True)
                    st.table(user_trade_by_admin)
                with cols[1]:
                    st.markdown("<h8 style='color: yellow;'>Bot</h8>", unsafe_allow_html=True)
                    st.table(user_bot_admin)
            st.markdown("<h3 style='color: Light Green;'>Business Volume</h3>", unsafe_allow_html=True)
            with ThreadPoolExecutor() as executor:
                future_get_binary_side_total = executor.submit(get_binary_side_total, username)

                future_rank = executor.submit(get_team_rank_table, False,username)
                future_left_with_spillover_deposits = executor.submit(total_user_team_deposit_left, True, username)
                future_left_without_spillover_deposits = executor.submit(total_user_team_deposit_left, False, username)
                future_total_user_team_deposit_right_with_spillover =  executor.submit(total_user_team_deposit_right, True,username)
                future_total_user_team_deposit_right_without_spillover = executor.submit(total_user_team_deposit_right, False,username)
                future_leader_wise_user_subscription = executor.submit(leader_wise_user_subscription, username)
                future_withdrawal_with_spillover =  executor.submit(get_total_user_team_withdrawal, True, username)
                future_withdrawal_without_spillover =  executor.submit(get_total_user_team_withdrawal, False, username)
                a1, a2, a3 ,a4,a5,a6= future_get_binary_side_total.result()
                rank = future_rank.result()
                e1,e2,e3= future_left_with_spillover_deposits.result()
                f1,f2,f3= future_left_without_spillover_deposits.result()
                total_user_team_deposit_right_with_spillover = future_total_user_team_deposit_right_with_spillover.result()
                g1,g2,g3 = future_total_user_team_deposit_right_with_spillover.result()
                h1,h2,h3 = future_total_user_team_deposit_right_without_spillover.result()
                total_user_team_deposit_right_without_spillover = future_total_user_team_deposit_right_without_spillover.result()
                package_details_admin, package_details_user,total_user_subscription_admin, total_user_subscription_user = future_leader_wise_user_subscription.result()
                
                total_users_left, total_users_right, total_left_withdrawal, total_right_withdrawal, user_list_left_side, user_list_right_side = future_withdrawal_with_spillover.result()
                
                total_users_left, total_users_right, total_left_withdrawal, total_right_withdrawal, user_list_left_side, user_list_right_side = future_withdrawal_without_spillover.result()

            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>Left Side</h6>", unsafe_allow_html=True)
                st.write(f'Binanry Volume : {a1}')
                st.write(f'Total Users Binanry Volume : {a2}')
                st.write(f'Total Admin Binanry Volume : {a3}')
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Right Side</h6>", unsafe_allow_html=True)
                st.write(f'Binanry Volume : {a4}')
                st.write(f'Total Users Binanry Volume : {a5}')
                st.write(f'Total Admin Binanry Volume : {a6}')
            st.markdown("<h3 style='color: yellow;'>Rank Volume</h3>", unsafe_allow_html=True)
            st.table(rank['Rank Details'])
            
            
            st.markdown("<h3 style='color: yellow;'>Team Desposit</h3>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>With Spillover Left</h6>", unsafe_allow_html=True)
                st.write(f'Total Amount : {e1}')
                st.write(f'Total Left Side Deposits User : {e2}')
                st.write(f'Total Left Side Deposits Admin : {e3}')
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Without Spillover Left</h6>", unsafe_allow_html=True)
                st.write(f'Total Amount : {f1}')
                st.write(f'Total Left Side Deposits User : {f2}')
                st.write(f'Total Left Side Deposits Admin : {f3}')
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>With Spillover Right</h6>", unsafe_allow_html=True)
                st.write(f'Total Amount : {g1}')
                st.write(f'Total Right Side Deposits User : {g2}')
                st.write(f'Total Right Side Deposits Admin : {g3}')
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Without Spillover Right</h6>", unsafe_allow_html=True)
                st.write(f'Total Amount : {h1}')
                st.write(f'Total Right Side Deposits User : {h2}')
                st.write(f'Total Right Side Deposits Admin : {h3}')
            
            
            st.markdown("<h3 style='color: yellow;'>Over All Subscription</h3>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>Admin</h6>", unsafe_allow_html=True)
                st.table(total_user_subscription_admin)
            with cols[1]:
                st.markdown("<h6 style='color: green;'>User</h6>", unsafe_allow_html=True)
                st.table(total_user_subscription_user)       
            
            
            st.markdown("<h3 style='color: yellow;'>User Wise Subscription</h3>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>Admin</h6>", unsafe_allow_html=True)
                if len(package_details_admin) == 0:
                    st.write("No Data Found")
                else:
                    df = pd.DataFrame(package_details_admin)
                    package_df = pd.json_normalize(df['Package']).fillna(0).astype(int)
                    result_df = pd.concat([df.drop(columns=["Package"]), package_df], axis=1)
                    st.dataframe(result_df.style.format(precision=0))
            with cols[1]:
                st.markdown("<h6 style='color: green;'>User</h6>", unsafe_allow_html=True)
                if len(package_details_user) == 0:
                    st.write("No Data Found")
                else:
                    df = pd.DataFrame(package_details_user)
                    package_df = pd.json_normalize(df['Package']).fillna(0).astype(int)
                    result_df = pd.concat([df.drop(columns=["Package"]), package_df], axis=1)
                    st.dataframe(result_df.style.format(precision=0))
           
           
           
            st.markdown("<h3 style='color: yellow;'>Team Withdrawal</h3>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>With Spilloweer Left Side</h6>", unsafe_allow_html=True)
                st.markdown(f'Total Users : {total_users_left}')
                st.markdown(f'Total Withdrawal : {total_left_withdrawal}')
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Without Spilloweer Left Side</h6>", unsafe_allow_html=True)
                st.markdown(f'Total Users : {total_users_left}')
                st.markdown(f'Total Withdrawal : {total_left_withdrawal}')
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>With Spilloweer Right Side</h6>", unsafe_allow_html=True)
                st.markdown(f'Total Users : {total_users_right}')
                st.markdown(f'Total Withdrawal : {total_right_withdrawal}')
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Without Spilloweer Right Side</h6>", unsafe_allow_html=True)
                st.markdown(f'Total Users : {total_users_right}')
                st.markdown(f'Total Withdrawal : {total_right_withdrawal}')


            st.markdown("<h3 style='color: yellow;'>Team Withdrawal</h3>", unsafe_allow_html=True)
            cols = st.columns(2)
            with cols[0]:
                st.markdown("<h6 style='color: green;'>Left Side</h6>", unsafe_allow_html=True)
                if len(user_list_left_side) == 0:
                    st.write("No Data Found")
                else:
                    df = pd.DataFrame(user_list_left_side)
                    df['Withdraw_Amount'] = df['Withdraw_Amount'].fillna(0).astype(int)
                    st.dataframe(df.style.format(precision=0))

            # Right Side
            with cols[1]:
                st.markdown("<h6 style='color: green;'>Right Side</h6>", unsafe_allow_html=True)
                if len(user_list_right_side) == 0:
                    st.write("No Data Found")
                else:
                    df = pd.DataFrame(user_list_right_side)
                    df['Withdraw_Amount'] = df['Withdraw_Amount'].fillna(0).astype(int)
                    st.dataframe(df.style.format(precision=0))

            

if st.session_state.logged_in == False:
    login(st,'Adminname','Password')
else:
    user_network()