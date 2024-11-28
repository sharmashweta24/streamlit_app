from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from core.db import *
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    combined_hierarchy = user_hierarchy_0 + user_hierarchy_1
    return combined_hierarchy, user_hierarchy_0, user_hierarchy_1
