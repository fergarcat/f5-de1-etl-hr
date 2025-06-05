## consumer.py
from kafka import KafkaConsumer
import json
import os
from dotenv import load_dotenv
from kafka_consumer.etl import process_message
from kafka_consumer.db_clients import sql, redis

load_dotenv()

consumer = KafkaConsumer(
    os.getenv("KAFKA_TOPIC"),
    bootstrap_servers=os.getenv("KAFKA_BROKER"),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id=os.getenv("KAFKA_GROUP_ID"),
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

REQUIRED_TYPES = {"personal", "location", "professional", "bank", "net"}

for message in consumer:
    raw_data = message.value
    user_id = raw_data.get("user_id") or raw_data.get("id")
    data_type = raw_data.get("type")

    if not user_id or not data_type or data_type not in REQUIRED_TYPES:
        continue

    redis.cache_partial(user_id, data_type, raw_data)
    cached = redis.retrieve_complete(user_id)

    if REQUIRED_TYPES.issubset(cached.keys()):
        transformed = {
            "user_id": user_id,
            "personal": cached.get("personal", {}),
            "location": cached.get("location", {}),
            "professional": cached.get("professional", {}),
            "bank": cached.get("bank", {}),
            "net": cached.get("net", {})
        }

        sql.store_transformed(transformed)
        redis.clear_cache(user_id)