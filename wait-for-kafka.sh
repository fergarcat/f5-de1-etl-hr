#!/bin/sh

# Espera hasta que Kafka esté disponible en host:port
# Uso: ./wait-for-kafka.sh kafka 29092

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for $host:$port..."

while ! nc -z "$host" "$port"; do
  sleep 1
done

echo "$host:$port is available, starting command..."
exec $cmd
