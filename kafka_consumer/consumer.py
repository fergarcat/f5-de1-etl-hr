import json
import os
import socket
import time
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka_consumer.etl import process_message
from kafka_consumer.db_clients import sql, redis
from kafka_consumer.db_clients.mongo import insert_raw_data
from config.logger_config import logger
from config import mongodb_config as mdb

#load_dotenv()

REQUIRED_TYPES = {
    "personal": {"email", "name", "passport", "sex", "telfnumber"},
    "location": {"address", "city", "postal_code"},
    "professional": {"company", "job", "company_email"},
    "bank": {"IBAN", "salary"},
    "net": {"IPv4"}
}

<<<<<<< Updated upstream
def safe_json_deserializer(m):
    if not m:
        logger.warning("⚠️ Mensaje vacío recibido.")
        return None
    try:
        return json.loads(m.decode('utf-8'))
    except Exception as e:
        logger.warning(f"⚠️ Error al deserializar mensaje: {m} - {e}")
        return None

def wait_for_kafka(host: str, port: int, timeout: int = 60):
    logger.info(f"⏳ Esperando a Kafka en {host}:{port}...")
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                logger.info("✅ Kafka está disponible.")
                return
        except OSError:
            if time.time() - start_time > timeout:
                logger.error(f"❌ Kafka no respondió tras {timeout} segundos.")
                raise TimeoutError("Kafka no disponible.")
            time.sleep(2)

=======
def safe_json_loads(m):
    try:
        return json.loads(m.decode('utf-8'))
    except (json.JSONDecodeError, AttributeError):
        return None

>>>>>>> Stashed changes
def run_consumer():
    logger.info("### CONSUMIDOR KAFKA INICIADO ###")

    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    kafka_host, kafka_port_str = kafka_broker.split(":")
    kafka_port = int(kafka_port_str)
    wait_for_kafka(kafka_host, kafka_port)

    try:
        consumer = KafkaConsumer(
<<<<<<< Updated upstream
            os.getenv("KAFKA_TOPIC"),
            bootstrap_servers=kafka_broker,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=os.getenv("KAFKA_GROUP_ID", "etl-group"),
            value_deserializer=safe_json_deserializer
=======
            #os.getenv("KAFKA_TOPIC"),
            'probando',
            #bootstrap_servers=os.getenv("KAFKA_BROKER"),
            bootstrap_servers = ['kafka:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id="etl-consumer-group",
            value_deserializer=lambda m: safe_json_loads(m)
>>>>>>> Stashed changes
        )
    except Exception as e:
        logger.error(f"❌ Error al crear el consumidor Kafka: {e}")
        return

    mongodb = mdb.MongoDbConnection()
    mongodb.connect()

    logger.info("🕒 Esperando mensajes...")

    for message in consumer:
        if message.value is None:
            logger.warning("⚠️ Mensaje vacío recibido, ignorando...")
            continue
        raw_data = message.value
        if raw_data is None:
            continue  # ignorar mensajes vacíos o mal deserializados

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

        logger.info(f"💾 Cacheando tipo '{data_type}' para user_id '{user_id}'")
        redis.cache_partial(user_id, data_type, raw_data)

        cached = redis.retrieve_complete(user_id)
        logger.info(f"📦 Datos cacheados para '{user_id}': {list(cached.keys())}")

        # Corregir la condición para verificar si el usuario tiene todos los tipos
        if REQUIRED_TYPES.keys() <= cached.keys():
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
