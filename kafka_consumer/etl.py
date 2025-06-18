import json
import os
from pymongo import MongoClient

# MongoDB setup
mongo_host = os.getenv("MONGO_HOST")
mongo_port = os.getenv("MONGO_PORT")

if not mongo_host or not mongo_port:
    raise EnvironmentError("Missing MONGO_HOST or MONGO_PORT environment variables")

mongo_client = MongoClient(
    host=os.getenv("MONGO_HOST", "localhost"),
    port=int(os.getenv("MONGO_PORT", 27017))
)
db_name = os.getenv("MONGODB_DB_NAME")  # or "MONGO_DB_NAME" depending on your fix choice
if not db_name:
    raise ValueError("❌ Environment variable MONGODB_DB_NAME is not set.")
mongo_db = mongo_client[db_name]
mongo_collection = mongo_db[os.getenv("MONGO_COLLECTION")]

def process_message(message):
    """
    Procesa un mensaje desde Kafka:
    - Lo guarda en MongoDB.
    """
    print(f"Procesando mensaje: {message}")

    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print("Mensaje no es JSON válido")
        return

    # Guardar en MongoDB
    mongo_collection.insert_one(data)
    print("Documento insertado en MongoDB")
