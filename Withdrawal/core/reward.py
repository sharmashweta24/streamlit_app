from os.path import abspath, join, dirname
from sys import path, exc_info

base_dir = abspath(join(dirname(__file__), "../"))
path.append(base_dir)
from collections import Counter, defaultdict
from core.db import *
from datetime import datetime


def rewards(username):

    binary_reward_find = network_rewards.find({"Username": username}, {'_id': 0})
    binary_reward_data = list(binary_reward_find) if binary_reward_find else []

    weekly_rewards_find = weekly_rewards.find({"Username": username}, {'_id': 0})
    weekly_rewards_data = list(weekly_rewards_find) if weekly_rewards_find else []

    compound_rewards_find = compound_rewards.find({"Username": username}, {'_id': 0})
    compound_rewards_data = list(compound_rewards_find) if compound_rewards_find else []

    rank_rewards_find = rank_rewards.find({"Username": username}, {'_id': 0})
    rank_rewards_data = list(rank_rewards_find) if rank_rewards_find else []

    rewards_find = {
        'Binary_Reward': binary_reward_data,
        'Weekly_Reward': weekly_rewards_data,
        'Compound_Reward': compound_rewards_data,
        'Rank_Reward': rank_rewards_data,
    }

    return rewards_find