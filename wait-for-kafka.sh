#!/bin/bash
# Esperar a que Kafka esté disponible

host="$1"
port="$2"

echo "⏳ Esperando a que Kafka ($host:$port) esté disponible..."

while ! nc -z "$host" "$port"; do
  sleep 1
done

echo "✅ Kafka está disponible"
shift 2
echo "🚀 Ejecutando comando: $@"
exec "$@"

