import os
from config.mongodb_config import db_connection
from config.logger_config import logger
from dotenv import load_dotenv

load_dotenv()

def insert_raw_data(data):
    try:
        db = db_connection.connect()
        collection_name = os.getenv("MONGO_COLLECTION")
        if not collection_name:
            raise ValueError("❌ MONGO_COLLECTION no está definida en .env")
        collection = db[collection_name]
        collection.insert_one(data)
        logger.info("📥 Documento insertado en MongoDB")
    except Exception as e:
        logger.error(f"❌ Error insertando en MongoDB: {e}")