from pymongo import MongoClient

from service.google import MONGO_TOKEN, init_google, get_secrets, MONGO_TOKEN_KEY

token = MONGO_TOKEN

if not token:
    init_google()
    token = get_secrets(MONGO_TOKEN_KEY)

# MongoDB connection setup
SERVICE_USER = "arbitragexiv-service-user"
CONNECTION_STRING = f"mongodb+srv://{SERVICE_USER}:{token}@tubalub.i3nux.mongodb.net/"
client = MongoClient(CONNECTION_STRING)
db = client['tubalub']
users_collection = db['users']


def get_client():
    return client


def get_db():
    return db


def get_collection(collection_name: str):
    return db[collection_name]
