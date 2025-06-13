import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
from config.logger_config import logger


load_dotenv()


class MongoDbConnection:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self) -> Database:
        if self._client is None:
            try:
                self._client = MongoClient(
                    os.getenv('MONGODB_URL'),
                    username=os.getenv('MONGO_INITDB_ROOT_USERNAME'),
                    password=os.getenv('MONGO_INITDB_ROOT_PASSWORD'),
                    serverSelectionTimeoutMS=5000
                )
                # Check if the connection is successful
                self._client.admin.command('ismaster')
                self._database = self._client[os.getenv('MONGODB_DB_NAME')]
                logger.info("✅ MongoDB connection established")
            except Exception as e:
                logger.error(f"❌ Error connectinig MongoDB: {e}")
                raise
        return self._database
    def get_collection(self, collection_name):
        return self.db[collection_name]
    def save_message_to_mongo(self, message_data):
        collection = self.get_collection(os.getenv('MONGODB_DBE'))
        collection.insert_one(message_data)
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("🔒 MongoDB connection closed")

# Global Instance
db_connection = MongoDbConnection()