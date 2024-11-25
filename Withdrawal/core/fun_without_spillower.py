from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)

from core.db import *

def get_user_without_spillover_users(username):
    without_spillover_users_list=[]
    without_spillover_users= user_network.find({'Username':username},{'_id':0,'Username':0})
    without_spillover_users = list(without_spillover_users)
    for i in without_spillover_users:
        for k, v in i.items():
            for user in v:
                user_side = user_details.find_one({"Username": user}, {"_id": 0, "Side": 1, "Sponsor": 1})
                sponsor = user_side.get('Sponsor')
                sponsor_side = user_side.get('Side')
                for entry in without_spillover_users_list:
                    if entry['Username'] == sponsor:
                        sponsor_side = entry['Side']
                        break
                data = {
                    "Username": user,
                    "Side": sponsor_side,
                }
                without_spillover_users_list.append(data)
    user_network_0 = []
    user_network_1 = []         
    for obj in without_spillover_users_list:
        if obj['Side']=='0':
            user_network_0.append(obj['Username'])
        else:
            user_network_1.append(obj['Username'])
    return without_spillover_users_list, user_network_0, user_network_1
