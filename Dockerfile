<<<<<<< Updated upstream
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
=======
FROM python:3.11
ENV PYTHONPATH="/app"

# Instalar netcat para wait-for-kafka.sh
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . /app

# Dar permisos de ejecución a scripts
RUN chmod +x /app/wait-for-kafka.sh
RUN chmod +x /app/entrypoint.sh
# Instalar ping para verificar conectividad
RUN apt-get update && apt-get install -y iputils-ping && rm -rf /var/lib/apt/lists/*


# Usamos ENTRYPOINT para esperar a Kafka
ENTRYPOINT ["/app/wait-for-kafka.sh", "kafka", "9092"]

# CMD serán los comandos que ejecutará entrypoint.sh una vez Kafka esté listo
CMD ["/app/entrypoint.sh"]
>>>>>>> Stashed changes
