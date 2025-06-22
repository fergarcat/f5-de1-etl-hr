# 🚀 Sistema ETL de Recursos Humanos - DataTech Solutions

> **Proyecto Formativo de Data Engineering:** Proceso ETL completo con dashboard web para gestión de datos de RRHH

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![Kafka](https://img.shields.io/badge/Apache-Kafka-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green.svg)
![Redis](https://img.shields.io/badge/Redis-Latest-red.svg)

## 📋 Descripción del Proyecto

Este es un **sistema ETL (Extract, Transform, Load) completo** diseñado para procesar datos de empleados en tiempo real. El proyecto combina múltiples tecnologías modernas para crear una pipeline robusta de procesamiento de datos con interfaz web interactiva.

### 🎯 Objetivos
- Procesar datos de empleados desde Kafka en tiempo real
- Almacenar datos en múltiples bases de datos (PostgreSQL, MongoDB, MySQL)
- Proporcionar un dashboard web moderno para visualización
- Implementar cache inteligente con Redis
- Generar analytics y reportes en tiempo real

### ✨ Características Principales
- ⚡ **Procesamiento en tiempo real** con Apache Kafka
- 🗄️ **Multi-base de datos:** PostgreSQL, MongoDB, MySQL, Redis
- 🌐 **Dashboard web moderno** con FastAPI + HTML/CSS/JS
- 📊 **Analytics interactivos** con Chart.js
- 🐳 **Containerización completa** con Docker Compose
- 🔄 **Pipeline ETL automatizada** con monitoreo
- 📱 **Interfaz responsive** y moderna

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Kafka Topic   │───▶│ ETL Consumer │───▶│   Databases     │
│  (HR Data)      │    │  (Python)    │    │ (Multi-DB)      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │                      │
                              ▼                      ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │  FastAPI Web    │◀───│  Redis Cache    │
                    │   Dashboard     │    │   (Temporal)    │
                    └─────────────────┘    └─────────────────┘
```

### 🔄 Flujo de Datos
1. **Extract:** Kafka consume mensajes con datos de empleados
2. **Transform:** ETL Consumer procesa y valida los datos
3. **Load:** Almacenamiento en PostgreSQL (principal) + MongoDB (raw) + MySQL (normalizado)
4. **Cache:** Redis almacena datos temporales para optimización
5. **Visualize:** Dashboard web muestra métricas en tiempo real

## 📁 Estructura Detallada del Proyecto

```
f5-de1-etl-hr/
├── 📄 README.md                     # Esta documentación
├── 📄 requirements.txt              # Dependencias Python
├── 📄 pyproject.toml               # Configuración del proyecto
├── 📄 docker-compose.yml           # Orquestación de servicios
├── 📄 Dockerfile                   # Imagen del ETL consumer
├── 📄 entrypoint.sh                # Script de inicio del container
├── 📄 run_fastapi.py               # Launcher para el dashboard
├── 📄 uv.lock                      # Lock file de dependencias
│
├── 📁 config/                      # ⚙️ Configuraciones
│   ├── 📄 __init__.py
│   ├── 📄 logger_config.py         # Configuración de logging
│   ├── 📄 logger_test.py           # Tests de logging
│   └── 📄 mongodb_config.py        # Config específica de MongoDB
│
├── 📁 fastapi/                     # 🌐 Aplicación Web (Dashboard)
│   ├── 📄 main.py                  # App principal FastAPI
│   │
│   ├── 📁 routers/                 # 🛣️ Rutas de la API
│   │   ├── 📄 __init__.py
│   │   ├── 📄 api.py               # Endpoints de datos y stats
│   │   └── 📄 frontend.py          # Rutas del frontend web
│   │
│   ├── 📁 templates/               # 📄 Templates HTML
│   │   ├── 📄 index.html           # Dashboard principal
│   │   └── 📄 analytics.html       # Página de analytics avanzados
│   │
│   └── 📁 static/                  # 🎨 Assets estáticos
│       ├── 📁 css/
│       │   └── 📄 style.css        # Estilos personalizados
│       ├── 📁 images/
│       │   └── 📄 DataTech Solutions.png # Logo corporativo
│       └── 📁 js/                  # JavaScript
│           ├── 📄 app.js           # Funciones principales del dashboard
│           ├── 📄 dashboard.js     # Lógica específica del dashboard
│           ├── 📄 analytics.js     # Analytics page logic
│           └── 📄 analytics_new.js # Analytics mejorados
│
├── 📁 kafka_consumer/              # ⚙️ Procesador ETL Principal
│   ├── 📄 __init__.py
│   ├── 📄 consumer.py              # Consumidor principal de Kafka
│   ├── 📄 etl.py                   # Lógica de transformación de datos
│   │
│   └── 📁 db_clients/              # 🗄️ Clientes de Bases de Datos
│       ├── 📄 __init__.py
│       ├── 📄 mongo_init.py        # Inicialización de MongoDB
│       ├── 📄 mongo.py             # Cliente MongoDB (datos raw)
│       ├── 📄 mysql_init.py        # Inicialización y modelos MySQL
│       ├── 📄 redis.py             # Cliente Redis (cache temporal)
│       └── 📄 sql.py               # Cliente PostgreSQL (datos finales)
│
├── 📁 sql/                         # 📊 Scripts SQL
│   └── 📄 init.sql                 # Scripts de inicialización de BD
│
├── 📁 notebooks/                   # 📓 Jupyter Notebooks (análisis)
│
└── 📁 tests/                       # 🧪 Tests
    └── 📄 test.py                  # Suite de pruebas
```

## 🛠️ Tecnologías Utilizadas

### Backend & ETL
- **Python 3.10+** - Lenguaje principal
- **Apache Kafka** - Streaming de datos en tiempo real
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para bases de datos relacionales
- **PyMongo** - Driver MongoDB para Python
- **Redis-py** - Cliente Redis para cache

### Bases de Datos
- **PostgreSQL** - Base de datos principal (datos procesados)
- **MongoDB** - Almacenamiento de datos raw/documentos
- **MySQL** - Base de datos normalizada (relacional)
- **Redis** - Cache en memoria para datos temporales

### Frontend & UI
- **HTML5/CSS3** - Estructura y estilos
- **JavaScript ES6+** - Lógica del frontend
- **Bootstrap 5** - Framework CSS responsive
- **Chart.js** - Gráficos interactivos
- **Font Awesome** - Iconografía

### DevOps & Infraestructura
- **Docker & Docker Compose** - Containerización
- **uv** - Gestor de dependencias Python moderno
- **dotenv** - Gestión de variables de entorno

## 🚀 Guía de Instalación y Ejecución

### Pre-requisitos
- Docker y Docker Compose instalados
- Python 3.10+ (para desarrollo local)
- Git (para clonar el repositorio)

### Paso 1: Clonar el Proyecto
```bash
git clone <repository-url>
cd f5-de1-etl-hr
```

### Paso 2: Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```bash
# Kafka Configuration
KAFKA_TOPIC=hr_data
KAFKA_GROUP_ID=hr_consumer_group
KAFKA_BROKER=kafka:9092

# MongoDB Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGODB_DB_NAME=hr_database
MONGO_COLLECTION=raw_employee_data
MONGO_HOST=mongo_consumer
MONGO_PORT=27017

# MySQL Configuration
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=hr_mysql
MYSQL_USER=hr_user
MYSQL_PASSWORD=hr_password
MYSQL_HOST=mysql_consumer

# PostgreSQL Configuration
POSTGRES_DB=hr_postgres
POSTGRES_USER=hr_user
POSTGRES_PASSWORD=hr_password
POSTGRES_HOST=postgres_consumer
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=redis_consumer
REDIS_PORT=6379
```

### Paso 3: Levantar el Sistema Completo

#### Opción A: Todo con Docker (Recomendado)
```bash
# Levantar todos los servicios
docker-compose up --build -d

# Ver logs del sistema
docker-compose logs -f etl_consumer
```

#### Opción B: Desarrollo Híbrido
```bash
# Solo bases de datos con Docker
docker-compose up -d mongo mysql redis

# FastAPI en local para desarrollo
cd fastapi
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# ETL Consumer en local
python -m kafka_consumer.consumer
```

### Paso 4: Acceder al Dashboard
- **Dashboard Principal:** http://localhost:8000
- **Analytics:** http://localhost:8000/analytics  
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 📊 Funcionalidades Detalladas

### 🎛️ Dashboard Principal (`/`)
- **Métricas en tiempo real:** Usuarios procesados, cache, sincronización
- **Gráficos interactivos:** Distribución por ciudades y posiciones
- **Monitor del pipeline:** Estado de Kafka → Transform → Load
- **Actividad reciente:** Últimos usuarios procesados
- **Estado del sistema:** Conexiones y salud de servicios

### 📈 Analytics Avanzados (`/analytics`)
- **KPIs del sistema:** Throughput, calidad de datos, pipelines activos
- **Métricas ETL:** Tipos de datos, timeline de procesamiento
- **Análisis de errores:** Categorización y severidad
- **Performance:** CPU, memoria, rates de procesamiento
- **Exportación de datos:** CSV, JSON con filtros

### 🔌 API Endpoints Principales

#### Estadísticas y Datos
- `GET /api/stats` - Estadísticas principales del dashboard
- `GET /api/users` - Lista paginada de usuarios
- `GET /api/cache/all` - Datos en cache de Redis
- `GET /api/analytics/summary` - Resumen analytics

#### Control del Pipeline
- `GET /api/pipeline/status` - Estado actual del pipeline
- `POST /api/pipeline/start` - Iniciar pipeline
- `POST /api/pipeline/stop` - Detener pipeline  
- `POST /api/pipeline/restart` - Reiniciar pipeline

#### Monitoreo
- `GET /api/health` - Health check de servicios
- `GET /api/realtime-metrics` - Métricas en tiempo real
- `GET /api/analytics/kpis` - KPIs del sistema

## 🔄 Proceso ETL Detallado

### 1. **Extract (Kafka Consumer)**
```python
# El consumer escucha el topic de Kafka
consumer = KafkaConsumer(
    'hr_data',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)
```

### 2. **Transform (Validación y Procesamiento)**  
```python
# Validación de tipos de datos requeridos
REQUIRED_TYPES = {
    "personal": {"email", "name", "passport", "sex", "telfnumber"},
    "location": {"address", "city", "postal_code"},
    "professional": {"company", "job", "company_email"},
    "bank": {"IBAN", "salary"},
    "net": {"IPv4"}
}
```

### 3. **Load (Multi-Database Storage)**
- **MongoDB:** Datos raw sin procesar
- **Redis:** Cache temporal para datos incompletos
- **PostgreSQL:** Datos finales procesados (JSON columns)
- **MySQL:** Datos normalizados (tablas relacionales)

### 4. **Monitor (Web Dashboard)**
- Visualización en tiempo real del estado
- Métricas de performance y errores
- Control manual del pipeline

## 🧪 Testing y Desarrollo

### Ejecutar Tests
```bash
# Tests básicos
python -m pytest tests/

# Test específico del logger
python config/logger_test.py

# Health check manual
curl http://localhost:8000/health
```

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# O usar uv (más rápido)
uv pip install -r requirements.txt

# Ejecutar solo el dashboard
python run_fastapi.py

# Ejecutar solo el consumer
python -m kafka_consumer.consumer
```

## 🛠️ Comandos Útiles

### Docker & Servicios
```bash
# Ver estado de containers
docker-compose ps

# Ver logs específicos
docker-compose logs kafka_consumer
docker-compose logs fastapi

# Reiniciar servicios
docker-compose restart etl_consumer

# Limpiar todo (¡cuidado con los datos!)
docker-compose down -v
docker system prune -f

# Acceder a un container
docker-compose exec etl_consumer bash
docker-compose exec mongo mongosh
```

### Base de Datos
```bash
# PostgreSQL
docker-compose exec postgres psql -U hr_user -d hr_postgres

# MongoDB
docker-compose exec mongo mongosh admin -u admin -p password123

# Redis
docker-compose exec redis redis-cli
```

### Logs y Debugging
```bash
# Logs en tiempo real
docker-compose logs -f --tail=100 etl_consumer

# Verificar configuración
docker-compose config

# Ver recursos utilizados
docker stats
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. **Error de conexión a Kafka**
```bash
# Verificar que Kafka esté corriendo
docker-compose logs kafka

# Verificar topics
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092
```

#### 2. **Error de bases de datos**
```bash
# Verificar conexiones
curl http://localhost:8000/api/health

# Reiniciar servicios de BD
docker-compose restart mongo mysql redis postgres
```

#### 3. **Dashboard no carga**
```bash
# Verificar FastAPI
curl http://localhost:8000/ping

# Ver logs del dashboard
docker-compose logs fastapi
```

#### 4. **Problemas de permisos**
```bash
# En Linux/Mac, ajustar permisos
chmod +x entrypoint.sh
sudo chown -R $USER:$USER ./data
```

### Variables de Entorno Faltantes
Si ves errores sobre variables de entorno, asegúrate de que el archivo `.env` esté presente y configurado correctamente.

### Performance Issues
- Verificar recursos de Docker: RAM mínimo 4GB recomendado
- Monitorear logs para identificar cuellos de botella
- Usar `docker stats` para ver uso de recursos

## 📈 Próximas Mejoras

### Corto Plazo
- [ ] Implementar autenticación y autorización
- [ ] Añadir más visualizaciones en analytics
- [ ] Implementar alertas automáticas
- [ ] Mejorar testing coverage

### Mediano Plazo  
- [ ] Integración con Apache Airflow
- [ ] Implementar data quality checks
- [ ] Añadir exportación de reportes
- [ ] Dashboard móvil nativo

### Largo Plazo
- [ ] Machine Learning para detección de anomalías
- [ ] Arquitectura de microservicios
- [ ] Implementación en cloud (AWS/GCP)
- [ ] Data lineage tracking

## 👨‍💻 Desarrollado por

**DataTech Solutions** - Especialistas en soluciones ETL y Data Engineering

### Tecnologías Core
- **Backend:** Python, FastAPI, SQLAlchemy
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Datos:** PostgreSQL, MongoDB, Redis, MySQL
- **Streaming:** Apache Kafka
- **DevOps:** Docker, Docker Compose

---

### 📞 Soporte y Contacto

Para preguntas, problemas o sugerencias:
- 📧 **Email:** soporte@datatech-solutions.com
- 🐛 **Issues:** [GitHub Issues](link-to-issues)
- 📚 **Docs:** [Documentación técnica](link-to-docs)

### 🔗 Enlaces Útiles
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Apache Kafka Guide](https://kafka.apache.org/documentation/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

**© 2024 DataTech Solutions - Sistema ETL para Recursos Humanos**
