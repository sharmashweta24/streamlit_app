import streamlit as st
from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
from collections import Counter, defaultdict
from core.db import *
from core import fun_without_spillower 
from core import fun_spillower

# USER DETAILS DATA
def get_user_details(username):
    user_deatils_find = user_details.find_one({'Username': username}, {'_id': 0, 'Username': 1, 'Name': 1, 'Country': 1, 'Sponsor': 1, 'Created_On': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$Created_On'}}})
    user_deatils_find['Date'] = user_deatils_find['Created_On']
    user_deatils_find.pop('Created_On')
    return user_deatils_find

# USER DEPOSIT DETAILS DATA
def get_user_deposite(username):
    deposits = list(user_deposit_transaction.find({'Username': username,'Status': 'SUCCESS'}, {'_id': 0}))
    user,admin=0,0
    for deposit in deposits:
        if deposit['By'] == 'User':
            user += float(deposit['USD_Recieved'])
        else:
            admin += float(deposit['USD_Recieved'])
    return user, admin

# USER user_subscription DATA
def get_user_subcription(username):
    subscription = list(user_subscription_qualification.find({'Username': username}, {'_id': 0, 'TransID': 1, 'Name': 1, 'Executed_By': 1, 'DateTime': {'$dateToString': {'format': '%Y-%m-%d %H:%M:%S', 'date': '$DateTime'}}}))
    return subscription

# USER user_subscription_TABLE
def get_user_sub(username):
    sub = list(user_subscription_qualification.find({'Username': username}, {'_id': 0, 'Trans_ID': 1, 'Name': 1,'Package_Type':1, 'Executed_By': 1}))
    user_trade_deatails = []
    user_bot_deatils = []
    for i in sub:
        if i['Package_Type'] == 'TRADE':
            user_trade_deatails.append(i)
        else:
            user_bot_deatils.append(i)
    user_trade_by_user = []
    user_trade_by_admin = []
    user_bot_user = []
    user_bot_admin = []
    for i in user_trade_deatails:
        if i['Executed_By'] == 'User':
            user_trade_by_user.append(i)
        else:
            user_trade_by_admin.append(i)
    for i in user_bot_deatils:
        if i['Executed_By'] == 'User':
            user_bot_user.append(i)
        else:
            user_bot_admin.append(i)
    return user_trade_deatails,user_bot_deatils,user_trade_by_user,user_trade_by_admin,user_bot_user,user_bot_admin

# USER DIRECT TEAM USER
def get_user_network(username):
    total_user = []
    user_direct = user_network.find({'Username': username}, {'_id': 0, 'Username': 0})
    user_network_list = list(user_direct)
    for i in user_network_list:
        for k, v in i.items():
            if isinstance(v, list):
                for user in v:
                    total_user.append(user)
            else:
                total_user.append(v)
    return total_user


def get_binary_side_total(username):
    total_user_business_volume_left = list(user_analytics.find(
        {'Username': {'$in': [username]}}, 
        {'_id': 0, 'Username': 1,'Binary_Business_0':1,'User_Binary_Business_0':1,
         'Admin_Binary_Business_0':1,'Binary_Business_1':1,'User_Binary_Business_1':1,'Admin_Binary_Business_1':1}))
    binary_bussiness_0 = total_user_business_volume_left[0]['Binary_Business_0']
    user_binary_bussiness_0 = total_user_business_volume_left[0]['User_Binary_Business_0']
    admin_binary_bussiness_0 = total_user_business_volume_left[0]['Admin_Binary_Business_0']
    binary_bussiness_1 = total_user_business_volume_left[0]['Binary_Business_1']
    user_binary_bussiness_1 = total_user_business_volume_left[0]['User_Binary_Business_1']
    admin_binary_bussiness_1 = total_user_business_volume_left[0]['Admin_Binary_Business_1']
    return binary_bussiness_0,user_binary_bussiness_0,admin_binary_bussiness_0,binary_bussiness_1,user_binary_bussiness_1,admin_binary_bussiness_1

# USER TOTAL TEAM AND BUISNESS VOLUM RIGHT
def get_binary_right_side_total(with_spillover, username):
    total_business_volume_trade_by_user_right = 0
    total_business_volume_trade_by_admin_right = 0
    total_business_volume_bot_by_user_right = 0
    total_business_volume_bot_by_admin_right = 0

    user_network_0 = []
    user_network_1 = []

    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)

    total_user_business_volume_right = list(user_subscription_qualification.find(
        {'Username': {'$in': user_network_1}},
        {'_id': 0, 'Username': 1, 'Price': 1, 'Package_Type': 1, 'Executed_By': 1}
    ))

    total_user_business_volume_right_list = len(total_user_business_volume_right)

    for record in total_user_business_volume_right:
        if record['Package_Type'] == 'TRADE':
            if record['Executed_By'] == 'User':
                total_business_volume_trade_by_user_right += float(record['Price'])
            else:
                total_business_volume_trade_by_admin_right += float(record['Price'])
        else:
            if record['Executed_By'] == 'User':
                total_business_volume_bot_by_user_right += float(record['Price'])
            else:
                total_business_volume_bot_by_admin_right += float(record['Price'])

    return (
        total_user_business_volume_right_list,
        total_business_volume_trade_by_user_right,
        total_business_volume_trade_by_admin_right,
        total_business_volume_bot_by_user_right,
        total_business_volume_bot_by_admin_right
    )

# USER SUBSCRIPTION QUALIFICATION LEFT SIDE DATA
def get_user_list_left_side(with_spillover,username):
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    
    total_user_left_side = user_subscription_qualification.find(
        {'Username': {'$in': user_network_0}}, 
        {'_id': 0, 'Username': 1, 'Name': 1, 'Executed_By': 1, 'Package_Type': 1}
    ).to_list(None)
    grouped_data = defaultdict(lambda: {'count': 0})
    for user in total_user_left_side:
        key = (user['Username'], user['Name'], user['Package_Type'], user['Executed_By'])
        grouped_data[key]['count'] += 1
        grouped_data[key].update(user) 

    user_data_left = []
    admin_data_left = []
    
    for data in grouped_data.values():
        entry = {
            'Username': data['Username'],
            'Name': data['Name'],
            'Package_Type': data['Package_Type'],
            'Executed_By': data['Executed_By'],
            'total': data['count']
        }
    
        if data['Executed_By'] == 'User':
            user_data_left.append(entry)
        else:
            admin_data_left.append(entry)

    return user_data_left, admin_data_left


# USER SUBSCRIPTION QUALIFICATION RIGHT SIDE
def get_user_list_right_side(with_spillover,username):
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    
    total_user_right_side = user_subscription_qualification.find(
        {'Username': {'$in': user_network_1}}, 
        {'_id': 0, 'Username': 1, 'Name': 1, 'Executed_By': 1, 'Package_Type': 1}
    ).to_list(None)

    grouped_data = defaultdict(lambda: {'count': 0})
    for user in total_user_right_side:
        key = (user['Username'], user['Name'], user['Package_Type'], user['Executed_By'])
        grouped_data[key]['count'] += 1
        grouped_data[key].update(user) 

    user_data_right = []
    admin_data_right = []
    
    for data in grouped_data.values():
        entry = {
            'Username': data['Username'],
            'Name': data['Name'],
            'Package_Type': data['Package_Type'],
            'Executed_By': data['Executed_By'],
            'total': data['count']
        }
    
        if data['Executed_By'] == 'User':
            user_data_right.append(entry)
        else:
            admin_data_right.append(entry)

    return user_data_right, admin_data_right

# USER TEAM RANK TABLE LEFT SIDE
from collections import Counter

# USER TEAM RANK TABLE LEFT SIDE
def get_team_rank_left(with_spillover, username):
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    
    team_rank_details = list(user_analytics.find(
        {'Username': {'$in': user_network_0}}, 
        {'_id': 0, 'Username': 1, 'Rank': 1}
    ))
    left_rank_counts = Counter([user['Rank'] for user in team_rank_details])
    
    # Create a dictionary with rank as the key and users with that rank as values
    left_user_rank_details = {}
    for user in team_rank_details:
        if user['Rank'] not in left_user_rank_details:
            left_user_rank_details[user['Rank']] = []
        left_user_rank_details[user['Rank']].append(user['Username'])
    
    return left_rank_counts, left_user_rank_details

# USER TEAM RANK TABLE RIGHT SIDE
def get_team_rank_right(with_spillover, username):
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    
    team_rank_details = list(user_analytics.find(
        {'Username': {'$in': user_network_1}}, 
        {'_id': 0, 'Username': 1, 'Rank': 1}
    ))

    right_rank_counts = Counter([user['Rank'] for user in team_rank_details])
    
    # Create a dictionary with rank as the key and users with that rank as values
    right_user_rank_details = {}
    for user in team_rank_details:
        if user['Rank'] not in right_user_rank_details:
            right_user_rank_details[user['Rank']] = []
        right_user_rank_details[user['Rank']].append(user['Username'])
    
    return right_rank_counts, right_user_rank_details

# USER TEAM RANK TABLE
def get_team_rank_table(with_spillover, username):
    left_ranks, left_user_rank_details = get_team_rank_left(with_spillover, username)
    right_ranks, right_user_rank_details = get_team_rank_right(with_spillover, username)

    all_ranks = set(left_ranks.keys()).union(right_ranks.keys())
    rank_table = {
        "Rank Details": []
    }

    for rank in sorted(all_ranks):
        if rank.lower() == "inten" or rank.lower() == "intern":
            continue

        left_count = left_ranks.get(rank, 0)
        right_count = right_ranks.get(rank, 0)

        # Get the users for this rank on the left and right side
        left_users = left_user_rank_details.get(rank, [])
        right_users = right_user_rank_details.get(rank, [])

        # Add the rank details along with users' names
        for user in left_users:
            rank_table["Rank Details"].append({
                "Username": user,
                "Rank": rank,
                "Left Side": left_count,
                "Right Side": right_count
            })
        
        for user in right_users:
            rank_table["Rank Details"].append({
                "Username": user,
                "Rank": rank,
                "Left Side": left_count,
                "Right Side": right_count
            })

    return rank_table




# USER TEAM TOTAL DEPOSIT LEFT
def total_user_team_deposit_left(with_spillover,username):
    total_left_side_deposits = 0
    total_user_team_deposits = 0
    total_admin_team_deposits = 0
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    # print("user_network_0",user_network_0)
    # print("user_network_1",user_network_1)
    deposits_left_total = list(user_deposit_transaction.find(
        {'Username': {'$in': user_network_0}, 'Status': 'SUCCESS'},
        {'_id': 0, 'USD_Recieved': 1, 'Username': 1, 'By': 1}  
    ))
    
    total_left_side_deposits = sum(i.get('USD_Recieved', 0) for i in deposits_left_total)

    for i in deposits_left_total:
        amount = float(i.get('USD_Recieved', 0))
        if i.get('By') == 'User':
            total_user_team_deposits += amount
        else:
            total_admin_team_deposits += amount


    return (total_left_side_deposits, total_user_team_deposits, total_admin_team_deposits)

# print(total_user_team_deposit_left(True,'chotadon'))

# USER TEAM TOTAL DEPOSIT RIGHT
def total_user_team_deposit_right(with_spillover,username):
    total_right_side_deposits = 0
    total_user_team_deposit_right = 0
    total_admin_team_deposit_right = 0
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    deposits_right_total =  list(user_deposit_transaction.find(
        {'Username': {'$in': user_network_1}, 'Status': 'SUCCESS'},
        {'_id': 0, 'USD_Recieved': 1, 'Username': 1, 'By': 1}  
    ))
    total_right_side_deposits = sum(i.get('USD_Recieved', 0) for i in deposits_right_total)

    for i in deposits_right_total:
        amount = float(i.get('USD_Recieved', 0))
        if i.get('By') == 'User':
            total_user_team_deposit_right += amount
        else:
            total_admin_team_deposit_right += amount
    return (total_right_side_deposits, total_user_team_deposit_right, total_admin_team_deposit_right)

# print(total_user_team_deposit_right(True,'chotadon'))
# USER TEAM DEPOSIT LEFT SIDE LIST
def get_user_team_deposit_left(with_spillover,username):
    user_team_deposits_user = []
    user_team_deposits_admin = []
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    deposits_left = user_deposit_transaction.find(
        {'Username': {'$in': user_network_0}, 'Status': 'SUCCESS'},
        {'_id': 0, 'USD_Recieved': 1, 'Username': 1, 'By': 1}  
    ).to_list(None)
    for i in deposits_left:
        if i['By'] == 'User':
            user_team_deposits_user.append(i)
        else:
            user_team_deposits_admin.append(i)
    return  user_team_deposits_user, user_team_deposits_admin

# USER TEAM DEPOSIT RIGHT SIDE LIST
def get_user_team_deposit_right(with_spillover,username):
    user_team_deposits_user = []
    user_team_deposits_admin = []
    user_network_0 = []
    user_network_1 = []
    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)
    deposits_right = user_deposit_transaction.find(
        {'Username': {'$in': user_network_1}, 'Status': 'SUCCESS'},
        {'_id': 0, 'USD_Recieved': 1, 'Username': 1, 'By': 1}  
    ).to_list(None)

    for i in deposits_right:
        if i['By'] == 'User':
            user_team_deposits_user.append(i)
        else:
            user_team_deposits_admin.append(i)

    return user_team_deposits_user, user_team_deposits_admin



def get_total_user_team_withdrawal(with_spillover, username):
    user_network_0 = []
    user_network_1 = []
    user_list_left_side = []
    user_list_right_side = []

    if with_spillover:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_spillower.get_users_network_binary(username)
    else:
        userwithout_spillover_users_list, user_network_0, user_network_1 = fun_without_spillower.get_user_without_spillover_users(username)

    left_side_withdrawals = list(user_wallet.aggregate([
        {'$match': {'Username': {'$in': user_network_0}}},
        {'$group': {'_id': '$Username', 'Withdraw_Amount': {'$sum': '$Withdraw_Amount'}}},
        {'$project': {'_id': 1, 'Withdraw_Amount': 1}}
    ]))

    right_side_withdrawals = list(user_wallet.aggregate([
        {'$match': {'Username': {'$in': user_network_1}}},
        {'$group': {'_id': '$Username', 'Withdraw_Amount': {'$sum': '$Withdraw_Amount'}}},
        {'$project': {'_id': 1, 'Withdraw_Amount': 1}}
    ]))

    total_users_left = len(user_network_0)
    total_users_right = len(user_network_1)
    total_left_withdrawal = sum(item.get('Withdraw_Amount', 0) for item in left_side_withdrawals)
    total_right_withdrawal = sum(item.get('Withdraw_Amount', 0) for item in right_side_withdrawals)

    user_list_left_side = [{'Username': item['_id'], 'Withdraw_Amount': item.get('Withdraw_Amount', 0)} for item in left_side_withdrawals]
    user_list_right_side = [{'Username': item['_id'], 'Withdraw_Amount': item.get('Withdraw_Amount', 0)} for item in right_side_withdrawals]

    user_list_left_side.sort(key=lambda x: x['Withdraw_Amount'], reverse=True)
    user_list_right_side.sort(key=lambda x: x['Withdraw_Amount'], reverse=True)

    return total_users_left, total_users_right, total_left_withdrawal, total_right_withdrawal, user_list_left_side, user_list_right_side






# Leader Wise user_details

def leader_wise_user_network(username):
        total_user = []

        user_direct = list(user_network.find({'Username': username}, {'_id': 0, 'Username': 0}))
        user_network_list = list(user_direct)
        for i in user_network_list:
            for k, v in i.items():
                if isinstance(v, list):
                    for user in v:
                        total_user.append(user)
                else:
                    total_user.append(v)


        return total_user

def leader_wise_user_deposit(username):
        total_user = leader_wise_user_network(username)
        user_deposit_list = user_deposit_transaction.find(  # Querying the collection
        {'Username': {'$in': total_user}, 'Status': 'SUCCESS', 'By': 'Admin'},
        {'_id': 0, 'USD_Recieved': 1}
    ).to_list(None)
        total_deposit = sum(float(i['USD_Recieved']) for i in user_deposit_list)
        user_deposit_data = {'Username': username, 'Total Deposit': total_deposit}
        return user_deposit_data

def leader_wise_user_withdrawal(username):
        total_user = leader_wise_user_network(username)
        user_withdrawal = list(user_wallet.find({'Username': {'$in': total_user}}, {'_id': 0, 'Username': 1, 'Total_Withdrawal': 1}))
        total_withdrawal = sum(float(i['Total_Withdrawal']) for i in user_withdrawal)
        user_withdrawal_data = {'Username': username, 'Total Withdrawal': total_withdrawal}
        return user_withdrawal_data


def leader_wise_user_subscription(username):
    total_user = leader_wise_user_network(username)

    # Fetching admin trade details
    trade_by_admin = list(user_subscription_qualification.aggregate([
        {'$match': {'Username': {'$in': total_user}, 'Executed_By': 'Admin', 'Package_Type': 'TRADE'}},
        {'$group': {
            '_id': '$Name',
            'Total': {'$sum': '$Price'},
            'Count': {'$sum': 1}
        }},
        {'$project': {
            '_id': 0,
            'Package': '$_id',
            'Total': 1,
            'Count': 1
        }}
    ]))

    # Fetching user trade details
    trade_by_user = list(user_subscription_qualification.aggregate([
        {'$match': {'Username': {'$in': total_user}, 'Executed_By': 'User', 'Package_Type': 'TRADE'}},
        {'$group': {
            '_id': '$Name',
            'Total': {'$sum': '$Price'},
            'Count': {'$sum': 1}
        }},
        {'$project': {
            '_id': 0,
            'Package': '$_id',
            'Total': 1,
            'Count': 1
        }}
    ]))

    # Fetching user bot details
    bot_by_user = list(user_subscription_qualification.aggregate([
        {'$match': {'Username': {'$in': total_user}, 'Executed_By': 'User', 'Package_Type': 'BOT'}},
        {'$group': {
            '_id': '$Name',
            'Total': {'$sum': '$Price'},
            'Count': {'$sum': 1}
        }},
        {'$project': {
            '_id': 0,
            'Package': '$_id',
            'Total': 1,
            'Count': 1
        }}
    ]))

    # Fetching admin bot details
    bot_by_admin = list(user_subscription_qualification.aggregate([
        {'$match': {'Username': {'$in': total_user}, 'Executed_By': 'Admin', 'Package_Type': 'BOT'}},
        {'$group': {
            '_id': '$Name',
            'Total': {'$sum': '$Price'},
            'Count': {'$sum': 1}
        }},
        {'$project': {
            '_id': 0,
            'Package': '$_id',
            'Total': 1,
            'Count': 1
        }}
    ]))

    # Calculating totals for each category
    total_trade_by_admin = sum(item['Total'] for item in trade_by_admin)

    total_trade_by_user = sum(item['Total'] for item in trade_by_user)

    total_bot_by_user = sum(item['Total'] for item in bot_by_user)

    total_bot_by_admin = sum(item['Total'] for item in bot_by_admin)

    return  trade_by_admin, trade_by_user, bot_by_user,bot_by_admin,total_trade_by_admin,total_trade_by_user,total_bot_by_user,total_bot_by_admin
    

def leader_wise_user_rank_deatails(username):
        total_user = leader_wise_user_network(username)
        rank_details = user_analytics.find(
            {'Username': username}, 
            {'_id': 0, 'Username': 1, 'Team_Rank_Qualified_1': 1, 'Team_Rank_Qualified_0': 1}
        ).to_list(None)
        rank_categories = [
            "Intern", "Team Leader", "Team Manager", "Senior Manager", 
            "Director", "Senior Director", "Global Director", 
            "President", "Senior President", "Global President", 
            "Crown President"
        ]

        team_rank_qualified_1_totals = {rank: 0 for rank in rank_categories}
        team_rank_qualified_0_totals = {rank: 0 for rank in rank_categories}

        for rank in rank_details:
            team_rank_qualified_1 = rank.get('Team_Rank_Qualified_1', {})
            team_rank_qualified_0 = rank.get('Team_Rank_Qualified_0', {})

            for category in rank_categories:
                if isinstance(team_rank_qualified_1, dict):
                    team_rank_qualified_1_totals[category] += team_rank_qualified_1.get(category, 0)
                if isinstance(team_rank_qualified_0, dict):
                    team_rank_qualified_0_totals[category] += team_rank_qualified_0.get(category, 0)

        rank_summary_table = [
            {
                "Rank Details": rank, 
                "Right_side": team_rank_qualified_1_totals[rank],
                "Left_side": team_rank_qualified_0_totals[rank]
            }
            for rank in rank_categories if rank != "Intern"
        ]

        return rank_summary_table


def matching_users(username):
        total_user = leader_wise_user_network(username)
        print(total_user)
        matching_level = list(user_matching.find(
            {'Username': {'$in': total_user}},
            {'_id': 0, 'Username': 1, 'Level': 1, 'Amount': 1}
        ))
        level_totals = {}  
        user_details_find1 = []  
        total_amount = 0 
        print(matching_level)
        for user in matching_level:
            user_details_find1.append({'Username': user['Username'], 'Level': user['Level']})
            amount = user.get('Amount', 0)
            level = user['Level']
            total_amount += amount  
            if level in level_totals:
                level_totals[level] += amount
            else:
                level_totals[level] = amount
        level_summary = [{"Level": f"Level{level}", "Total": total} for level, total in level_totals.items()]
        level_summary.sort(key=lambda x: int(x['Level'].replace('Level', '')))
        level_summary.append({"Level": "Total", "Total": total_amount})
        # print(level_summary)
        # print(user_details_find1)
        return user_details_find1, level_summary

