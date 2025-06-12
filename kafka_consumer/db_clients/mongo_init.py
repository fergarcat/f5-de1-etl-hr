## mongo.py
from config import mongodb_config as mdb
from dotenv import load_dotenv
#from config.logger_config import logger as Logger
from pymongo import MongoClient
import os
load_dotenv()

try:
    mongo_db = mdb.MongoDbConnection()
    mongo_db.connect()
    #Logger.info("✅ MongoDB connection established")
    collection = mongo_db.db.create_collection(os.getenv("MONGO_COLLECTION_NAME"))
    mongo_db.db.create_collection("mi_coleccion")


    #Logger.info(f"✅ Collection '{os.getenv('MONGO_COLLECTION_NAME')}' created or accessed successfully")
except Exception as e:
    #Logger.error(f"❌ Error connecting to MongoDB: {e}")
    raise e
