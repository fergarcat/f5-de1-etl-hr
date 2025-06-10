from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv
import socket

load_dotenv()

def running_in_docker():
    # Opción 1: si defines una variable especial en Docker, ej: IN_DOCKER=1
    if os.getenv("IN_DOCKER") == "1":
        return True
    
    # Opción 2: intentar detectar si el hostname es el nombre del contenedor Docker
    hostname = socket.gethostname()
    # Por ejemplo, si el hostname es diferente a lo habitual, o contiene "app" (ajusta según tu caso)
    # Aquí una comprobación simple, puedes personalizar:
    return hostname == "etl_consumer"  # o el nombre real de tu contenedor

if running_in_docker():
    kafka_broker = os.getenv("KAFKA_BROKER", "kafka:29092")
else:
    kafka_broker = "localhost:9092"  # broker local para desarrollo

print(f"Usando Kafka broker: {kafka_broker}")

producer = KafkaProducer(
    bootstrap_servers=kafka_broker,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

test_messages = [
    {
        "user_id": "user1",
        "type": "personal",
        "name": "Alice",
        "age": 30
    },
    {
        "user_id": "user1",
        "type": "location",
        "city": "Madrid",
        "country": "Spain"
    },
    {
        "user_id": "user1",
        "type": "professional",
        "position": "Engineer",
        "company": "CompanyX"
    },
    {
        "user_id": "user1",
        "type": "bank",
        "account": "1234567890",
        "bank": "BankY"
    },
    {
        "user_id": "user1",
        "type": "net",
        "social": "twitter",
        "handle": "@alice"
    }
]

topic = os.getenv("KAFKA_TOPIC", "probando")

for message in test_messages:
    producer.send(topic, message)
    print(f"Mensaje enviado: {message}")

producer.flush()
