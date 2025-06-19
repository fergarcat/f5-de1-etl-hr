# Usa la imagen oficial de python 3.10 slim
FROM python:3.10-slim

# Establece variables de entorno para evitar problemas con debconf
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Actualiza pip
RUN pip install --upgrade pip

# Copia el archivo de dependencias
COPY requirements.txt /app/requirements.txt

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copia todo el código fuente
COPY . /app

# Asegura permisos
RUN chmod +x /app/entrypoint.sh

# Usa usuario no root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Ejecuta el script como punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]

# Asegura directorio de logs
RUN mkdir -p /app/logs && chmod -R 777 /app/logs