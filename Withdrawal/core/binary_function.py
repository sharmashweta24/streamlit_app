from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = 'mongodb+srv://doadmin:0ZeKg6Q321x79G4t@db-mongodb-fra1-25085-01-421631d0.mongo.ondigitalocean.com/'
DATABASE_NAME = 'OdecenstTestClone'

def connect_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[DATABASE_NAME]

db = connect_database()

async def fetch_binary(username, username2):
    binary_collection = db['Binary_Location']
    settings_collection = db['Settings']

    sponsor = await binary_collection.find_one(
        {'Username': username},
        {'_id': 0, 'Location': 1}
    )
    if not sponsor:
        return {'msg': f"User {username} is invalid"}, 305

    loc = sponsor['Location']

    settings = await settings_collection.find_one({}, {'_id': 0, 'Binary_Level': 1})
    if not settings:
        return {'msg': "Binary_Level setting not found"}, 305

    count = settings['Binary_Level']
    if count == 0:
        return {"msg": "Binary Level is greater than 200"}, 305

    user_analytics = []
    original_loc = loc  # Store the original location for correct truncation

    while len(loc) > 0 and count > 0:
        user = await binary_collection.find_one(
            {'Location': loc},
            {'_id': 0, 'Username': 1}
        )
        if user:
            user_analytics.append({
                'Username': user.get('Username'),
                'Binary Level': 200 - count,
                'Location': loc
            })
        loc = loc[:-1]  # Truncate location correctly
        count -= 1
        if user and user['Username'] == username2:
            break

    if any(user['Username'] == username2 for user in user_analytics):
        return user_analytics, 200
    else:
        return {'msg': "Please check username"}, 305

async def main(username, username2):
    return await fetch_binary(username, username2)
