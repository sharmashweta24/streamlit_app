
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

MONGODB_URL = 'mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/'
DATABASE_NAME = 'OdecenstTestClone'

def connect_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

db = connect_database()

async def fetch_binary(username,username2):
    binary_collection = db['Binary_Location']
    settings_collection = db['Settings']
    analytics_collection = db['User_Analytics']
    sponsor = await binary_collection.find_one(
        {'Username': username},
        {'_id': 0, 'Location': 1}
    )
    if not sponsor:
        print(f"User {username} is invalid")
        message={
                'msg':f"User {username} is invalid"
        }
        return message,305
    loc = sponsor['Location']
    print("Sponsor Location:", loc)
    settings = await settings_collection.find_one({}, {'_id': 0, 'Binary_Level': 1})
    if not settings:
        print("Binary_Level setting not found")
        message={
            'msg':f"Binary_Level setting not found"
        }
        return message,305
    count = settings['Binary_Level']
    if count == 0:
        return {"msg":"Binary Level is greater than 200"},305
    else:
        user_analytic = await analytics_collection.find_one(
            {'Username': username},
            {
                    '_id': 0,
                    'Total_Direct': 1,
                    'Total_Team': 1,
                    'Rank_Business': 1,
                    'Binary_Business': 1
                }
        )
        user_analytics = []   
        while len(loc) > 1 and count > 0:
            user = await binary_collection.find_one(
                {'Location': loc[:-1]},
                {'_id': 0, 'Username': 1}
            )
            print("loc",loc)
            print("User:", user)
            
            if user:  
                user_analytics.append(user.get('Username')) 
            loc = loc[:-1]
            count -= 1
            dd=200-count
            print("binary_level:",dd)
            if user['Username']==username2:
                break
        if username2 in user_analytics:
            return dd,200
        else:
            res={
                'msg':"PLease check username"
            }
            return res,305

async def main(username,username2):
    data,status= await fetch_binary(username,username2)
    print("User Data:", data)
    if status == 200:
        print("Data:", data)
    elif status == 305:
        print(data)

username = "shanzleader18"
username2="admin"

asyncio.run(main(username,username2))














# import streamlit as st
# import asyncio
# from motor.motor_asyncio import AsyncIOMotorClient

# MONGODB_URL = 'mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/'
# DATABASE_NAME = 'OdecenstTestClone'

# def connect_database():
#     client = AsyncIOMotorClient(MONGODB_URL)
#     return client[DATABASE_NAME]

# db = connect_database()

# async def fetch_binary(username, username2):
#     binary_collection = db['Binary_Location']
#     settings_collection = db['Settings']

#     sponsor = await binary_collection.find_one(
#         {'Username': username},
#         {'_id': 0, 'Location': 1}
#     )
#     if not sponsor:
#         return {'msg': f"User {username} is invalid"}, 305

#     loc = sponsor['Location']

#     settings = await settings_collection.find_one({}, {'_id': 0, 'Binary_Level': 1})
#     if not settings:
#         return {'msg': "Binary_Level setting not found"}, 305

#     count = settings['Binary_Level']
#     if count == 0:
#         return {"msg": "Binary Level is greater than 200"}, 305

#     user_analytics = []
#     original_loc = loc  # Store the original location for correct truncation

#     while len(loc) > 0 and count > 0:
#         user = await binary_collection.find_one(
#             {'Location': loc},
#             {'_id': 0, 'Username': 1}
#         )
#         if user:
#             user_analytics.append({
#                 'Username': user.get('Username'),
#                 'Binary Level': 200 - count,
#                 'Location': loc
#             })
#         loc = loc[:-1]  # Truncate location correctly
#         count -= 1
#         if user and user['Username'] == username2:
#             break

#     if any(user['Username'] == username2 for user in user_analytics):
#         return user_analytics, 200
#     else:
#         return {'msg': "Please check username"}, 305

# async def main(username, username2):
#     return await fetch_binary(username, username2)

# # Streamlit integration
# st.title("Binary Location Tracker")

# username = st.text_input("Enter Sponsor Username:", value="shanzleader18")
# username2 = st.text_input("Enter Target Username:", value="admin")

# if st.button("Fetch Data"):
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     data, status = loop.run_until_complete(main(username, username2))

#     if status == 200:
#         st.write(f"**Sponsor Location:** {data[0]['Location']}")
#         st.write(f"**Users in Binary Tree:** {len(data)}")
#         st.write("**User Data:**")
#         st.table(data)
#     else:
#         st.error(data['msg'])
