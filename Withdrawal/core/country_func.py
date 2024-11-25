from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
from collections import Counter, defaultdict
from core.db import *
from datetime import datetime


def user_deatils_data(country):
    by_user_data = []
    by_admin_data = []

    user_find = user_details.find(
        {'Country': country},
        {'_id': 0, 'Username': 1, 'Country': 1, 'Registered_By': 1}
    )
    user_find = list(user_find)

    for i in user_find:
        if i['Registered_By'] == 'User':
            by_user_data.append(i['Username'])
        else:
            by_admin_data.append(i['Username'])
    return by_user_data, by_admin_data


def get_country(country):
    user_country = user_details.find({'Country': country}, {'_id': 0, 'Username': 1, 'Country': 1})
    user_country = list(user_country)
    return user_country
def get_rank(country):
    by_user_data, by_admin_data = user_deatils_data(country)

    user_rank_find = user_analytics.find(
        {'Username': {'$in': by_user_data}, 'Rank': {'$ne': 'Intern'}},
        {'Rank': 1, 'Username': 1, '_id': 0}
    )
    user_rank_find_admin = user_analytics.find(
        {'Username': {'$in': by_admin_data}, 'Rank': {'$ne': 'Intern'}},
        {'Rank': 1, 'Username': 1, '_id': 0}
    )
    user_rank_find = list(user_rank_find)

    user_rank_find_admin = list(user_rank_find_admin)

    return user_rank_find, user_rank_find_admin

def rank_subscription_earning(country):
    by_user_data, by_admin_data = user_deatils_data(country)

    cursor1 = user_analytics.find(
        {
            'Username': {'$in': by_admin_data},
            'Current_Rank_Business_0': {'$ne': 0},
            'Current_Rank_Business_1': {'$ne': 0}
        },
        {
            'Current_Rank_Business_0': 1,
            'Current_Rank_Business_1': 1,
            'Username': 1,
            '_id': 0
        }
    )
    cursor2 = user_analytics.find(
        {
            'Username': {'$in': by_user_data},
            'Current_Rank_Business_0': {'$ne': 0},
            'Current_Rank_Business_1': {'$ne': 0}
        },
        {
            'Current_Rank_Business_0': 1,
            'Current_Rank_Business_1': 1,
            'Username': 1,
            '_id': 0
        }
    )
    results = list(cursor1)
    results1=list(cursor2)
    return results,results1


def binanry_subscription_earning(country):
    by_user_data, by_admin_data = user_deatils_data(country)
    cursor1 = user_analytics.find(
        {
            'Username': {'$in': by_admin_data},
            'Current_Binary_Business_0': {'$ne': 0},
            'Current_Binary_Business_1': {'$ne': 0}
        },
        {
            'Current_Binary_Business_0': 1,
            'Current_Binary_Business_1': 1,
            'Username': 1,
            '_id': 0
        }
    )
    cursor2 = user_analytics.find(
        {
            'Username': {'$in': by_user_data},
            'Current_Binary_Business_0': {'$ne': 0}, 
            'Current_Binary_Business_1': {'$ne': 0}
        },
        {
            'Current_Binary_Business_0': 1,
            'Current_Binary_Business_1': 1,
            'Username': 1,
            '_id': 0
        }
    )
    results = list(cursor1)
    results1=list(cursor2)
    return results,results1


def user_calculate_deposits(country):
    by_user_data, by_admin_data = user_deatils_data(country)
    
    deposits = list(user_deposit_transaction.find(
        {'Username': {'$in': by_user_data}, 'Status': 'SUCCESS'},
        {'USD_Recieved': 1, 'Username': 1, '_id': 0}
    ))
    deposits_admin = list(user_deposit_transaction.find(
        {'Username': {'$in': by_admin_data}, 'Status': 'SUCCESS'},
        {'USD_Recieved': 1, 'Username': 1, '_id': 0}
    ))

    user_totals = {}
    for deposit in deposits:
        username = deposit['Username']
        usd_received = deposit['USD_Recieved']
        user_totals[username] = user_totals.get(username, 0) + usd_received
    
    total_by_user = sum(user_totals.values())

    admin_totals = {}
    for deposit in deposits_admin:
        username = deposit['Username']
        usd_received = deposit['USD_Recieved']
        admin_totals[username] = admin_totals.get(username, 0) + usd_received
    
    total_by_admin = sum(admin_totals.values())

    for username, total in user_totals.items():
        print(f"{username}: {total}")
    
    for username, total in admin_totals.items():
        print(f"{username}: {total}")

    return {
        'total_by_user': total_by_user,
        'user_details': user_totals,
        'total_by_admin': total_by_admin,
        'admin_details': admin_totals
    }
