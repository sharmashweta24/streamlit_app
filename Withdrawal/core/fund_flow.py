from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
from collections import Counter, defaultdict
from core.db import *
from datetime import datetime

def fund_flow_details(username):
    pipeline = [
        {"$match": {"Username": username, "Status": "SUCCESS"}},
        {
            "$project": {
                "_id": 0,
                "USD_Recieved": 1,
                "By": 1,
                "Gateway": 1,
                "DateTime": {"$dateToString": {"format": "%Y-%m-%d", "date": "$DateTime"}}
            }
        }
    ]
    money_flow_find = list(user_deposit_transaction.aggregate(pipeline))
    if not money_flow_find: 
        return [] 
    return money_flow_find 

def user_subscription(username):
    pipeline = [
        {"$match": {"Username": username}},
        {
            "$project": {
                "_id": 0,
                "Name": 1,
                "Price": 1,
                "Executed_By": 1,
                "DateTime": {"$dateToString": {"format": "%Y-%m-%d", "date": "$DateTime"}}
            }
        }
    ]
    subscription_find = list(user_subscription_qualification.aggregate(pipeline))
    
    if not subscription_find:  
        return []
    
    return subscription_find

def user_money_flow(username):
    money_flow_data = fund_flow_details(username)

    exclude_wallet_types = ['Commission_Balance', 'Rank_Reward', 'Binary_Earning_Balance', 'Subscription_Balance','ROI_Balance', 'Matching_Income_Balance','Withdrawal_Balance']

    money_flow_data = user_deposit_transaction.find(
        {"Username": username, "Status": "SUCCESS"},
        {
            "_id": 0,
            'Username': 1,
        }
    )
    transaction_data = list(
        money_transaction.find(
            {"Username": {'$in': [i['Username'] for i in money_flow_data]}},
            {
                "_id": 0, "Username": 1, "Amount": 1, 'From': 1, 'To': 1, "Executed_By": 1,
                "From_Wallet_Type": 1, "To_Wallet_Type": 1, "Transaction": 1, "DateTime": {"$dateToString": {"format": "%Y-%m-%d", "date": "$DateTime"}}
            }
        )
    )

    filtered_transaction_data = [
        transaction for transaction in transaction_data
        if transaction.get("From_Wallet_Type") not in exclude_wallet_types and transaction.get("To_Wallet_Type") not in exclude_wallet_types
    ]

    to_users = [transaction['To'] for transaction in filtered_transaction_data if 'To' in transaction]

    sorted_money_flow = sorted(money_flow_data, key=lambda x: x.get("DateTime", ""))

    result = {
        "Money_Flow": sorted_money_flow,
        "Money_Transactions": filtered_transaction_data,
        "To_Users": to_users 
    }

    return result
 
def to_details(username):
    to_details_find = user_money_flow(username)

    valid_users = []

    for transaction in to_details_find["Money_Transactions"]:
        to_user = transaction['To']
        if fund_flow_details(to_user):  
            valid_users.append(to_user)
    # print(valid_users)
    return valid_users
to_details('chotadon')

def all_user_details(username):
    to_users = to_details(username) 
    
    all_users_info = {}

    for to_user in to_users:
        user_fund_flow = fund_flow_details(to_user)
        user_sub = user_subscription(to_user)
        user_money_flow_data = user_money_flow(to_user)

        all_users_info[to_user] = {
            "Fund_Flow": user_fund_flow,
            "Subscription": user_sub,
            "Money_Transactions": user_money_flow_data["Money_Transactions"]
        }

    return all_users_info


