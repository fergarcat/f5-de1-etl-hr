#!/bin/sh

# echo "Esperando a Kafka en $1:$2 ..."
# ./wait-for-kafka.sh "$1" "$2"

echo "Ejecutando scripts de inicialización..."
python kafka_consumer/db_clients/mongo_init.py
python kafka_consumer/db_clients/mysql_init.py

echo "Lanzando consumidor principal..."
python kafka_consumer/consumer.py
