from kafka import KafkaConsumer
import json
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Inicializamos el consumidor Kafka
consumer = KafkaConsumer(
    'probando',
    bootstrap_servers='localhost:29092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='etl-consumer-debug'
)

logging.info("🔎 Escuchando mensajes en el topic 'probando'...")

# Diccionario para registrar tipos por usuario
user_fields = {}

for msg in consumer:
    data = msg.value
    user_id = data.get("user_id")
    data_type = data.get("type")

    if not user_id or not data_type:
        logging.warning(f"Mensaje inválido: {data}")
        continue

    if user_id not in user_fields:
        user_fields[user_id] = set()

    user_fields[user_id].add(data_type)

    logging.info(f"👤 Usuario: {user_id} → Tipos recibidos hasta ahora: {sorted(user_fields[user_id])}")
