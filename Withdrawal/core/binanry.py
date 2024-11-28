from concurrent.futures import ThreadPoolExecutor, as_completed
from core.db import *

def find_users_recursively(username, side, user_hierarchy):
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
            
def get_users_network_binary(username):
    user_hierarchy_0 = []
    user_hierarchy_1 = []
    main_user_data = user_binary.find_one({'Username': username}, {'_id': 0, '0': 1, '1': 1})
    if main_user_data:
        with ThreadPoolExecutor() as executor:  
            if '0' in main_user_data and main_user_data['0']:
                executor.submit(find_users_recursively, main_user_data['0'], 0, user_hierarchy_0)
            if '1' in main_user_data and main_user_data['1']:
                executor.submit(find_users_recursively, main_user_data['1'], 1, user_hierarchy_1)
    a = list(user_analytics.find({'Username': {'$in': user_hierarchy_0}}, {'_id': 0, 'Username': 1,'Admin_Binary_Business_0': 1,'Admin_Binary_Business_1': 1,'User_Binary_Business_0':1,'User_Binary_Business_1':1}))
    b = list(user_analytics.find({'Username': {'$in': user_hierarchy_1}}, {'_id': 0, 'Username': 1, 'Admin_Binary_Business_0': 1,'Admin_Binary_Business_1': 1,'User_Binary_Business_0':1,'User_Binary_Business_1':1}))
    return  a+b

# get_users_network_binary("laksh001")

