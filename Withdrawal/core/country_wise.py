from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
from collections import Counter, defaultdict
from core.db import *
from datetime import datetime
from collections import defaultdict

def country_total():
    country_wise_user = user_details.find({},{'Country':1,'_id':0})
    country_wise_user = list(country_wise_user)
    country_count = {}
    
    for user in country_wise_user:
        country = user.get('Country')
        if country:
            if country in country_count:
                country_count[country] += 1
            else:
                country_count[country] = 1
    
    return country_count


def country_wise(country):
    by_user_data = []
    by_admin_data = []
    country_find = user_details.find({'Country': country}, {'_id': 0,'Username': 1, 'Registered_By': 1,'Country': 1})
    country_find = list(country_find)

    for i in country_find:
        if i['Registered_By'] == 'User':
            by_user_data.append(i['Username'])
        else:
            by_admin_data.append(i['Username'])
    
    return by_user_data, by_admin_data

def user_calculate_deposits(country):
    by_user_data, by_admin_data = country_wise(country)
    total_user = 0
    total_admin = 0
    
    user_deposites = user_deposit_transaction.find(
        {'Username': {'$in': by_user_data + by_admin_data}, 'Status': 'SUCCESS'},
        {'_id': 0, 'Username': 1, 'USD_Recieved': 1, 'By': 1}
    )
    user_deposites = list(user_deposites)

    user_details = {}
    admin_details = {}

    for i in user_deposites:
        if i['By'] == 'User':
            total_user += float(i['USD_Recieved'])
            user_details[i['Username']] = float(i['USD_Recieved'])
        else:
            total_admin += float(i['USD_Recieved'])
            admin_details[i['Username']] = float(i['USD_Recieved'])

    return {
        'user_details': user_details,
        'admin_details': admin_details,
        'total_user': total_user,
        'total_admin': total_admin
    }

def get_subscription(country):
    trade_summary = defaultdict(lambda: {'by_user': 0, 'by_admin': 0})
    bot_summary = defaultdict(lambda: {'by_user': 0, 'by_admin': 0})

    by_user_data, by_admin_data = country_wise(country)
    
    package_details_admin = user_subscription_qualification.find({
        'Username': {'$in': by_admin_data + by_user_data} 
    }, {'_id': 0, 'Name': 1, 'Package_Type': 1, 'Price': 1, 'Executed_By': 1})
    package_details_admin = list(package_details_admin)
    
    for i in package_details_admin:
        name = i['Name']
        package_type = i['Package_Type']
        price = i['Price']
        executed_by = i['Executed_By']

        if package_type == 'TRADE':
            if executed_by == 'Admin':
                trade_summary[name]['by_admin'] += price
            else:
                trade_summary[name]['by_user'] += price
        elif package_type == 'BOT':
            if executed_by == 'Admin':
                bot_summary[name]['by_admin'] += price
            else:
                bot_summary[name]['by_user'] += price

    trade_data = dict(trade_summary)
    bot_data = dict(bot_summary)

    return trade_data, bot_data

def get_rank(country):
    by_user_data, by_admin_data = country_wise(country)
    user_rank_find = user_analytics.find({'Username': {'$in': by_user_data + by_admin_data}}, {'Rank': 1, 'Username': 1, '_id': 0})
    user_rank_find = list(user_rank_find)
    rank_counts = {}
    exclude_ranks = ['intern']
    for user in user_rank_find:
        rank = user.get('Rank', '').lower() 

        if rank and rank not in exclude_ranks:
            if rank in rank_counts:
                rank_counts[rank] += 1 
            else:
                rank_counts[rank] = 1  

    return rank_counts

def get_matching_details(country):
    by_user_data, by_admin_data = country_wise(country)
    user_matching_data = user_matching.find({'Username': {'$in': by_user_data + by_admin_data}}, {'_id': 0, 'Username': 1, 'Level': 1})
    user_matching_data = list(user_matching_data)
    for i in user_matching_data:
        i['Amount'] = float(i['Amount'])


    return user_matching_data

def get_withdrawal_details(country):
    by_user_data, by_admin_data = country_wise(country)
    withdrawal_data = list(withdrawl_request.find({'Username': {'$in': by_user_data + by_admin_data},"Status":"APPROVED"}, {'_id': 0, 'Username': 1, 'Amount': 1}))
    total_withdrawal = sum(float(i['Amount']) for i in withdrawal_data)
    user_withdrawal_data = {'Country': country, 'Total Withdrawal': total_withdrawal}
    return user_withdrawal_data
