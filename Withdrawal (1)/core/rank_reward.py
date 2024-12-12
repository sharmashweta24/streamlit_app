from datetime import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# MongoDB connection setup
client = MongoClient('mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin')
db = client['Odecent_B']
col1 = db['Rank_Reward_Transaction']
col3 = db['Subscription_Qualification']

def process_record(record):
    """Process each record and add the 'Admin' flag."""
    rr = col3.find_one({'Username': record['Username'], 'Executed_By': 'Admin'}, {'_id': 0})
    if rr and rr.get('ROI_Distribution', False) == True:
        record['Admin'] = True
    else:
        record['Admin'] = False
    return record

def fetch_transactions(start_date, end_date):
    """Fetch transactions from MongoDB starting from the selected date."""
    transactions = col1.find({'DateTime': {'$gt': datetime.combine(start_date, datetime.min.time())}}, {'_id': 0})
    return list(transactions)

def process_transactions(transactions):
    """Process all transactions in parallel."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_record, transactions))
    return results

def generate_csv(df, filename):
    """Generates a CSV file from the DataFrame."""
    df.to_csv(filename, index=False)
