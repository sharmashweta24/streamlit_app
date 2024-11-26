import pymongo


client = pymongo.MongoClient("mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/")
db = client["OdecenstTestClone"]
# client = pymongo.MongoClient("mongodb+srv://doadmin:E2963A08R7TCep5Z@db-mongodb-fra1-94403-0fe401bc.mongo.ondigitalocean.com/?authSource=admin")
# db = client['Odecent_B'] 

user_details = db["User_Details"]
user_network = db["User_Network"]
user_deposit_transaction = db["Deposit_Transaction"]
user_matching_income_transaction = db["Matching_Income_Transaction"]
user_analytics = db["User_Analytics"]
user_subscription_qualification = db["Subscription_Qualification"]
user_wallet = db["User_Wallet"]
user_binary = db["Binary_Location"]
admin = db["Admin"]
user_matching = db["Matching_Income_Transaction"]
col1 = db['Withdrawal_Request']
col2 = db['User_Wallet']
col3 = db['Withdrawal_Transactions']
col4 = db['Admin']
network_rewards = db["Binary_Transaction"]
weekly_rewards = db["ROI_Transaction"]
compound_rewards = db["Compounding_Transactions"]
rank_rewards = db["Rank_Reward_Transaction"]
direct_rewards = db["Commission_Transaction"]
money_transaction=db["Money_Transaction"]
withdrawl_request  = db['Withdrawal_Request']



deposite_collection = db["Deposit_Transaction"]
subscription_earning_collection = db["Subscription_Earning_Transactions"]
country = db['Country']