FROM python:3.10-slim
ENV PYTHONPATH="/app"

# Instalar netcat para el script wait-for-kafka.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*
# Copiar requisitos y luego instalar dependencias
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . /app

# Dar permisos de ejecución al script
RUN chmod +x wait-for-kafka.sh

# Comando que espera a Kafka y luego lanza el consumer
CMD ["./wait-for-kafka.sh", "kafka", "29092", "python", "kafka_consumer/consumer.py"]
