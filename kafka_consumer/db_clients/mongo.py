## mongo.py
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_url = f"mongodb://{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/"
db_name = os.getenv("MONGO_DB")
collection_name = os.getenv("MONGO_COLLECTION")

client = MongoClient(mongo_url)
db = client[db_name]
collection = db[collection_name]

def insert_raw_data(data):
    collection.insert_one(data)