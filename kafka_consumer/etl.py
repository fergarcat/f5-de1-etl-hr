import json
import os
from pymongo import MongoClient

# MongoDB setup
mongo_client = MongoClient(host=os.getenv("MONGO_HOST"), port=int(os.getenv("MONGO_PORT")))
mongo_db = mongo_client[os.getenv("MONGO_DB")]
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
