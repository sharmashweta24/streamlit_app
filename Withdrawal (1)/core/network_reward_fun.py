from datetime import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor

# MongoDB connection setup
client = MongoClient('mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin')
db = client['Odecent_B']
col1 = db['Binary_Transaction']
col2 = db['User_Analytics']
col3 = db['Subscription_Qualification']

def process_record1(record):
    """Processes each record and adds the 'Admin' flag."""
    cc = col2.find_one({'Username': record['Username']}, {'_id': 0})
    rr = col3.find_one({'Username': record['Username'], 'Executed_By': 'Admin'}, {'_id': 0})
    if cc:
        if cc['Admin_Binary_Business'] > 0 or rr:
            record['Admin'] = True
        else:
            record['Admin'] = False
    return record

# def login(username, password):
#     """Handles the login validation."""
#     if username == 'admin' and password == 'admin123':  # Replace with your actual validation logic
#         return True
#     return False

def fetch_transactions(start_date, end_date):
    """Fetches transactions based on the start date."""
    transactions = col1.find({'DateTime': {'$gt': datetime.combine(start_date, datetime.min.time())}}, {'_id': 0})
    return list(transactions)

def process_transactions(transactions):
    """Processes all transactions in parallel."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_record1, transactions))
    return results
