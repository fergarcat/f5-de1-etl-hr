# Usa la imagen oficial de python 3.10 slim
FROM python:3.10-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY requirements.txt /app/requirements.txt

# Instala las dependencias de Python
RUN apt-get update && apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia todo el código fuente (incluyendo config y kafka_consumer)
COPY . /app

# Comando por defecto al iniciar el contenedor
CMD ["python", "-m", "kafka_consumer.consumer"]
