# kafka_producer.py

import json
import time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Usa kafka:9092 si corres desde dentro de Docker
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

messages = [
    {"user_id": "u123", "type": "personal", "name": "Juan", "email": "juan@test.com", "passport": "A123", "sex": "M", "telfnumber": "123456789"},
    {"user_id": "u123", "type": "location", "address": "Calle Falsa 123", "city": "Madrid", "postal_code": "28001"},
    {"user_id": "u123", "type": "professional", "company": "Empresa S.A.", "job": "Developer", "company_email": "juan@empresa.com"},
    {"user_id": "u123", "type": "bank", "IBAN": "ES9121000418450200051332", "salary": "3000"},
    {"user_id": "u123", "type": "net", "IPv4": "192.168.1.1"}
]

for msg in messages:
    producer.send("probando", msg)
    print(f"Mensaje enviado: {msg}")
    time.sleep(1)

producer.flush()
producer.close()
