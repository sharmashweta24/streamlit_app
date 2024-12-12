from concurrent.futures import ThreadPoolExecutor, as_completed
from core.db import *
import pandas as pd

def find_users_recursively(username, side, user_hierarchy):
    try:
        user_data = user_binary.find_one({'Username': username}, {'_id': 0, '0': 1, '1': 1})
        if not user_data:
            return
        user_hierarchy.append(username)
        tasks = []
        with ThreadPoolExecutor() as executor:
            if '0' in user_data and user_data['0']:
                tasks.append(executor.submit(find_users_recursively, user_data['0'], 0, user_hierarchy))
            if '1' in user_data and user_data['1']:
                tasks.append(executor.submit(find_users_recursively, user_data['1'], 1, user_hierarchy))
            for future in as_completed(tasks):
                future.result()
    except Exception as e:
        print(f"Error in find_users_recursively: {e}")

def get_users_network_binary(username):
    user_hierarchy_0 = []
    user_hierarchy_1 = []
    
    try:
        # Get main user data
        main_user_data = user_binary.find_one({'Username': username}, {'_id': 0, '0': 1, '1': 1})
        
        if main_user_data:
            with ThreadPoolExecutor() as executor:  
                tasks = []
                if '0' in main_user_data and main_user_data['0']:
                    tasks.append(executor.submit(find_users_recursively, main_user_data['0'], 0, user_hierarchy_0))
                if '1' in main_user_data and main_user_data['1']:
                    tasks.append(executor.submit(find_users_recursively, main_user_data['1'], 1, user_hierarchy_1))
                for future in as_completed(tasks):
                    future.result()

        # Fetch analytics data
        analytics_query = user_analytics.find(
            {'Username': {'$in': user_hierarchy_0 + user_hierarchy_1}},
            {
                '_id': 0,
                'Username': 1,
                'Admin_Binary_Business_0': 1,
                'Admin_Binary_Business_1': 1,
                'User_Binary_Business_0': 1,
                'User_Binary_Business_1': 1
            }
        )
        analytics_data = list(analytics_query)

        # Fetch total user data
        total_user = user_analytics.find_one(
            {'Username': username},
            {
                '_id': 0,
                'Admin_Binary_Business_0': 1,
                'Admin_Binary_Business_1': 1,
                'User_Binary_Business_0': 1,
                'User_Binary_Business_1': 1
            }
        )
        
        # Create a DataFrame for the analytics data
        df = pd.DataFrame(analytics_data)
        df.rename(columns={
            'Admin_Binary_Business_0': 'Admin Binary Business (Left Side)',
            'Admin_Binary_Business_1': 'Admin Binary Business (Right Side)',
            'User_Binary_Business_0': 'User Binary Business (Left Side)',
            'User_Binary_Business_1': 'User Binary Business (Right Side)'
        }, inplace=True)

        # Create a DataFrame for the total user data
        if total_user:
            total_user_df = pd.DataFrame([total_user])
            total_user_df.rename(columns={
                'Admin_Binary_Business_0': 'Total Admin Left Side',
                'Admin_Binary_Business_1': 'Total Admin Right Side',
                'User_Binary_Business_0': 'Total User Left Side',
                'User_Binary_Business_1': 'Total User Right Side'
            }, inplace=True)
        else:
            total_user_df = pd.DataFrame()

        return df, total_user_df

    except Exception as e:
        print(f"Error in get_users_network_binary: {e}")
        return pd.DataFrame(), pd.DataFrame()
