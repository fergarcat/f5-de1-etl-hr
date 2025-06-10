# producer_test_full.py
from kafka import KafkaProducer
import json
import time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

user_id = "123"
types_data = {
    "location": {"city": "Madrid", "country": "España"},
    "professional": {"job": "Ingeniero", "experience": 5},
    "bank": {"account": "ES7620770024003102575766", "balance": 2500},
    "net": {"email": "juan@example.com", "ip": "192.168.1.1"}
}

for tipo, datos in types_data.items():
    mensaje = {
        "user_id": user_id,
        "type": tipo,
        "data": datos
    }
    producer.send('probando', mensaje)
    print(f"✅ Enviado: {tipo}")
    time.sleep(1)

producer.flush()
