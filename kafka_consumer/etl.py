## etl.py
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from datetime import datetime
from config import mongodb_config 
from dotenv import load_dotenv
load_dotenv()
import os

# 1. CONEXIÓN A MONGODB
mongo_client = mongodb_config.MongoDbConnection()
mongo_client.connect()
mongo_db = mongo_client[os.getenv("MONGODB_DB_NAME")]
mongo_collection = mongo_db[os.getenv("MONGODB_COLLECTION")]

# 2. CONEXIÓN A MYSQL
mysql_uri = "mysql+mysqlconnector://usuario:contraseña@localhost/mi_base"
engine = create_engine(mysql_uri)

# 3. LECTURA DE DATOS DESDE MONGODB
documentos = list(mongo_collection.find())

# 4. CARGA EN MYSQL
with engine.begin() as conn:
    for doc in documentos:
        nombre = doc.get("nombre", "sin_nombre")
        ts = doc.get("timestamp")
        
        # Asegurar formato datetime
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except Exception:
                ts = None
        
        # Insertar en MySQL
        conn.execute(
            text("INSERT INTO eventos (nombre, timestamp) VALUES (:nombre, :timestamp)"),
            {"nombre": nombre, "timestamp": ts}
        )

print(f"✅ {len(documentos)} documentos migrados a MySQL.")
