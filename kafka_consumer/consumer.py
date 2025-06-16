# consumer.py

import json
import os
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka_consumer.etl import process_message
from kafka_consumer.db_clients import sql, redis
from kafka_consumer.db_clients.mongo import insert_raw_data
from config.logger_config import logger
from config import mongodb_config as mdb

load_dotenv()

REQUIRED_TYPES = {
    "personal": {"email", "name", "passport", "sex", "telfnumber"},
    "location": {"address", "city", "postal_code"},
    "professional": {"company", "job", "company_email"},
    "bank": {"IBAN", "salary"},
    "net": {"IPv4"}
}

def run_consumer():
    logger.info("### CONSUMIDOR KAFKA INICIADO ###")

    try:
        consumer = KafkaConsumer(
            os.getenv("KAFKA_TOPIC"),
            bootstrap_servers=os.getenv("KAFKA_BROKER"),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=os.getenv("KAFKA_GROUP_ID"),
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
    except Exception as e:
        logger.error(f"❌ Error al crear el consumidor Kafka: {e}")
        return
    mongodb = mdb.MongoDbConnection()
    mongodb.connect()
    for message in consumer:
        raw_data = message.value
        mongodb.save_message_to_mongo(raw_data)
        logger.info(f"📥 Mensaje recibido: {raw_data}")


        try:
            insert_raw_data(raw_data)
        except Exception as e:
            logger.warning(f"⚠️ Error insertando en MongoDB: {e}")

        
        user_id = raw_data.get("user_id") or raw_data.get("id")
        data_type = raw_data.get("type")

        if not user_id or not data_type or data_type not in REQUIRED_TYPES:
            logger.warning(f"⚠️ Mensaje inválido: user_id={user_id}, type={data_type}")
            continue

        # Cachear
        logger.info(f"💾 Cacheando tipo '{data_type}' para user_id '{user_id}'")
        redis.cache_partial(user_id, data_type, raw_data)

        cached = redis.retrieve_complete(user_id)
        logger.info(f"📦 Datos cacheados para '{user_id}': {list(cached.keys())}")

        if REQUIRED_TYPES.issubset(cached.keys()):
            logger.info(f"✅ Usuario '{user_id}' completo. Procesando ETL...")

            transformed = {
                "user_id": user_id,
                "personal": cached.get("personal", {}),
                "location": cached.get("location", {}),
                "professional": cached.get("professional", {}),
                "bank": cached.get("bank", {}),
                "net": cached.get("net", {})
            }

            # ETL opcional
            # transformed = process_message(transformed)

            sql.store_transformed(transformed)
            logger.info(f"📤 Usuario '{user_id}' almacenado en SQL.")
            redis.clear_cache(user_id)

if __name__ == "__main__":
    run_consumer()
