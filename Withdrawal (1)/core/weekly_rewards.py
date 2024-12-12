from datetime import datetime
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

# MongoDB connection setup
client = MongoClient('mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin')
db = client['Odecent_B']
col1 = db['ROI_Transaction']
col3 = db['Subscription_Qualification']

def process_record(record):
    """Process each record and add the 'Admin' flag and col3's DateTime."""
    rr = col3.find_one({'Username': record['Username'], 'Executed_By': 'Admin'}, {'_id': 0, 'DateTime': 1, 'ROI_Distribution': 1})
    if rr:
        record['Admin'] = rr.get('ROI_Distribution', False)
        record['Col3_DateTime'] = rr.get('DateTime', None).strftime('%Y-%m-%d %H:%M:%S') if rr.get('DateTime') else None
    else:
        record['Admin'] = False
        record['Col3_DateTime'] = None
    
    record['Processed_DateTime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    return record
def fetch_transactions(start_date, end_date):
    """Fetch transactions from MongoDB starting from the selected date."""
    transactions = col1.find({'DateTime': {'$gt': datetime.combine(start_date,datetime.min.time())}}, {'_id': 0})
    return list(transactions)

def process_transactions(transactions):
    """Process all transactions in parallel."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_record, transactions))
    return results
