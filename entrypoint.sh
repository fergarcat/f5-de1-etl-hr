#!/bin/sh

echo "Ejecutando scripts de inicialización..."
python -m kafka_consumer.db_clients.mongo_init
python -m kafka_consumer.db_clients.mysql_init
echo "Lanzando consumidor principal..."
python -m kafka_consumer.consumer