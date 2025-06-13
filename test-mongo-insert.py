# test_mongo_insert.py
from kafka_consumer.db_clients.mongo import insert_raw_data

data = {"user_id": "testuser", "type": "personal", "name": "Prueba"}
insert_raw_data(data)
