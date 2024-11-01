import os

from pymongo import MongoClient

SERVICE_USER = "arbitragexiv-service-user"
SERVICE_PASSWORD = os.getenv("MONGO_SERVICE_PASSWORD")

CONNECTION_STRING = f"mongodb+srv://{SERVICE_USER}:{SERVICE_PASSWORD}@tubalub.i3nux.mongodb.net/"

client = MongoClient(CONNECTION_STRING)
