# ========================================
# API.PY - ENDPOINTS PARA OBTENER DATOS
# ========================================
"""
Este archivo define todos los endpoints que devuelven datos JSON
para que el JavaScript del dashboard pueda crear gráficos

FLUJO:
1. JavaScript hace petición: fetch('/api/stats')
2. Este archivo lee MongoDB  
3. Devuelve JSON con estadísticas
4. JavaScript usa esos datos para crear gráficos
"""

# ========================================
# IMPORTS - LIBRERÍAS NECESARIAS
# ========================================
from fastapi import APIRouter, HTTPException
import os
import random
from datetime import datetime
from dotenv import load_dotenv

# Importar clientes de bases de datos
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    print("⚠️ MySQL connector no disponible")
    MYSQL_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    print("⚠️ Redis no disponible")
    REDIS_AVAILABLE = False

# ========================================
# CONFIGURACIÓN INICIAL
# ========================================
load_dotenv()
api_router = APIRouter()  # Crear router para agrupar endpoints

# ========================================
# IMPORTAR CONFIGURACIONES MONGODB
# ========================================
# Intentar importar conexión a MongoDB, si no existe usar datos mock
try:
    from config.mongodb_config import db_connection
    from config.logger_config import logger
    MONGODB_AVAILABLE = True
    print("✅ MongoDB configurado correctamente")
except ImportError as e:
    print(f"⚠️ MongoDB no disponible: {e}")
    print("📝 Usando datos MOCK para desarrollo")
    db_connection = None
    logger = None
    MONGODB_AVAILABLE = False

# ========================================
# CONFIGURACIÓN DE BASES DE DATOS
# ========================================

# Configuración MongoDB (datos raw desde Kafka)
MONGO_CONFIG = {
    'database': os.getenv('MONGODB_DB_NAME', 'etl_db'),
    'collection': os.getenv('MONGO_COLLECTION', 'raw_data')
}

# Configuración MySQL (datos estructurados/relacionales)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'database': os.getenv('MYSQL_DATABASE', 'hr'),
    'user': os.getenv('MYSQL_USER', 'mysql_f5_de1'),
    'password': os.getenv('MYSQL_PASSWORD', '3tL_f542')
}

# Configuración Redis (cache temporal)
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'redis'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': 0
}

def get_mongodb():
    """
    FUNCIÓN PARA CONECTAR A MONGODB
    - Intenta conectar a MongoDB para datos raw
    - Si no puede, devuelve None y usará datos mock
    """
    try:
        if db_connection and MONGODB_AVAILABLE:
            db = db_connection.connect()
            return db[MONGO_CONFIG['collection']]
        return None
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to MongoDB: {e}")
        print(f"❌ Error MongoDB: {e}")
        return None

def get_mysql_connection():
    """
    FUNCIÓN PARA CONECTAR A MYSQL
    - Conecta a MySQL para datos estructurados
    - Se usa para consultas más complejas y relacionales
    """
    try:
        if MYSQL_AVAILABLE:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        return None
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to MySQL: {e}")
        print(f"❌ Error MySQL: {e}")
        return None

def get_redis_connection():
    """
    FUNCIÓN PARA CONECTAR A REDIS
    - Conecta a Redis para cache temporal
    - Mejora el rendimiento de consultas frecuentes
    """
    try:
        if REDIS_AVAILABLE:
            r = redis.Redis(**REDIS_CONFIG)
            r.ping()  # Test connection
            return r
        return None
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to Redis: {e}")
        print(f"❌ Error Redis: {e}")
        return None

# ========================================
# ENDPOINTS PRINCIPALES - DASHBOARD
# ========================================

@api_router.get("/health")
async def health():
    """
    HEALTH CHECK - VERIFICAR QUE LA API FUNCIONA
    Endpoint: GET /api/health
    
    Verifica conexiones a:
    - MongoDB (datos raw)
    - MySQL (datos estructurados) 
    - Redis (cache)
    
    Respuesta:
    {
        "status": "OK",
        "databases": {
            "mongodb": "connected" | "disconnected",
            "mysql": "connected" | "disconnected", 
            "redis": "connected" | "disconnected"
        },
        "timestamp": "2024-12-20T10:30:00"
    }
    """
    health_status = {
        "status": "OK",
        "databases": {},
        "timestamp": datetime.now().isoformat()
    }
    
    # Test MongoDB connection
    try:
        collection = get_mongodb()
        if collection is not None:
            collection.count_documents({})
            health_status["databases"]["mongodb"] = "connected"
        else:
            health_status["databases"]["mongodb"] = "disconnected"
    except:
        health_status["databases"]["mongodb"] = "error"
    
    # Test MySQL connection
    try:
        conn = get_mysql_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            health_status["databases"]["mysql"] = "connected"
        else:
            health_status["databases"]["mysql"] = "disconnected"
    except:
        health_status["databases"]["mysql"] = "error"
    
    # Test Redis connection
    try:
        r = get_redis_connection()
        if r is not None:
            r.ping()
            health_status["databases"]["redis"] = "connected"
        else:
            health_status["databases"]["redis"] = "disconnected"
    except:
        health_status["databases"]["redis"] = "error"
    
    return health_status

@api_router.get("/stats")
async def get_dashboard_stats():
    """
    ESTADÍSTICAS PRINCIPALES PARA EL DASHBOARD
    Endpoint: GET /api/stats
    
    FLUJO DE DATOS:
    1. Intentar obtener datos desde MySQL (datos estructurados)
    2. Si no está disponible, usar MongoDB (datos raw)
    3. Si no está disponible, usar datos MOCK
    
    Este endpoint es usado por dashboard.js para:
    - Mostrar total de empleados procesados
    - Crear gráfico de distribución por ciudades
    - Crear gráfico de distribución por departamentos
    
    Respuesta:
    {
        "total_employees": 1250,
        "avg_salary": 65750.50,
        "top_cities": [{"city": "Madrid", "count": 345}, ...],
        "top_departments": [{"department": "IT", "count": 285}, ...],
        "data_source": "mysql" | "mongodb" | "mock",
        "status": "success"
    }
    """
    try:
        print("📊 Obteniendo estadísticas del dashboard...")
        
        # OPCIÓN 1: Intentar obtener datos desde MySQL (estructurados)
        mysql_conn = get_mysql_connection()
        if mysql_conn is not None:
            print("🔗 Usando datos desde MySQL...")
            return await get_stats_from_mysql(mysql_conn)
        
        # OPCIÓN 2: Si MySQL no está disponible, usar MongoDB (raw)
        collection = get_mongodb()
        if collection is not None:
            print("🔗 Usando datos desde MongoDB...")
            return await get_stats_from_mongodb(collection)
        
        # OPCIÓN 3: Si no hay bases de datos, usar datos MOCK
        print("🔗 Usando datos MOCK...")
        return await get_mock_stats()
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting dashboard stats: {e}")
        print(f"❌ Error en stats: {e}")
        # Si hay error, usar datos MOCK
        return await get_mock_stats()

async def get_stats_from_mysql(conn):
    """
    OBTENER ESTADÍSTICAS DESDE MYSQL
    - Datos ya estructurados y procesados
    - Consultas SQL más eficientes
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Total empleados
        cursor.execute("SELECT COUNT(*) as total FROM employees")
        total_result = cursor.fetchone()
        total_employees = total_result['total'] if total_result else 0
        
        # 2. Salario promedio
        cursor.execute("SELECT AVG(salary) as avg_salary FROM employees WHERE salary IS NOT NULL")
        salary_result = cursor.fetchone()
        avg_salary = round(salary_result['avg_salary'], 2) if salary_result and salary_result['avg_salary'] else 0
        
        # 3. Top 5 ciudades
        cursor.execute("""
            SELECT city, COUNT(*) as count 
            FROM employees 
            WHERE city IS NOT NULL 
            GROUP BY city 
            ORDER BY count DESC 
            LIMIT 5
        """)
        cities_data = cursor.fetchall()
        top_cities = [{"city": row['city'], "count": row['count']} for row in cities_data]
        
        # 4. Top 5 departamentos
        cursor.execute("""
            SELECT department, COUNT(*) as count 
            FROM employees 
            WHERE department IS NOT NULL 
            GROUP BY department 
            ORDER BY count DESC 
            LIMIT 5
        """)
        departments_data = cursor.fetchall()
        top_departments = [{"department": row['department'], "count": row['count']} for row in departments_data]
        
        conn.close()
        
        return {
            "total_employees": total_employees,
            "avg_salary": avg_salary,
            "top_cities": top_cities,
            "top_departments": top_departments,
            "last_updated": datetime.now().isoformat(),
            "data_source": "mysql",
            "status": "success"
        }
        
    except Exception as e:
        print(f"❌ Error en MySQL: {e}")
        conn.close()
        raise e

async def get_stats_from_mongodb(collection):
    """
    OBTENER ESTADÍSTICAS DESDE MONGODB
    - Datos raw desde Kafka
    - Usar agregaciones de MongoDB
    """
    # 1. TOTAL DE EMPLEADOS PROCESADOS
    total_employees = collection.count_documents({})
    print(f"📈 Total empleados en MongoDB: {total_employees}")
    
    # 2. TOP 5 CIUDADES CON MÁS EMPLEADOS
    # Buscar en el campo: location.city
    cities_pipeline = [
        {"$match": {"location.city": {"$exists": True, "$ne": None}}},  # Solo docs con ciudad
        {"$group": {"_id": "$location.city", "count": {"$sum": 1}}},    # Agrupar por ciudad
        {"$sort": {"count": -1}},                                       # Ordenar por cantidad
        {"$limit": 5}                                                   # Solo top 5
    ]
    cities_data = list(collection.aggregate(cities_pipeline))
    top_cities = [{"city": c["_id"], "count": c["count"]} for c in cities_data]
    
    # 3. TOP 5 DEPARTAMENTOS CON MÁS EMPLEADOS  
    # Buscar en el campo: professional.department
    departments_pipeline = [
        {"$match": {"professional.department": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": "$professional.department", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    departments_data = list(collection.aggregate(departments_pipeline))
    top_departments = [{"department": d["_id"], "count": d["count"]} for d in departments_data]
    
    # 4. SALARIO PROMEDIO
    salary_pipeline = [
        {"$match": {"professional.salary": {"$exists": True, "$ne": None}}},
        {"$group": {"_id": None, "avg_salary": {"$avg": "$professional.salary"}}}
    ]
    salary_data = list(collection.aggregate(salary_pipeline))
    avg_salary = round(salary_data[0]["avg_salary"], 2) if salary_data else 0
    
    return {
        "total_employees": total_employees,
        "avg_salary": avg_salary,
        "top_cities": top_cities,
        "top_departments": top_departments,
        "last_updated": datetime.now().isoformat(),
        "data_source": "mongodb",
        "status": "success"
    }

# ========================================
# ENDPOINTS ANALYTICS - GRÁFICOS AVANZADOS
# ========================================

@api_router.get("/analytics/salary-by-location")
async def get_salary_by_location():
    """
    ANÁLISIS DE SUELDOS POR UBICACIÓN
    Endpoint: GET /api/analytics/salary-by-location
    
    Para crear gráficos de barras o mapas con:
    - Salario promedio por ciudad
    - Número de empleados por ciudad
    
    Respuesta:
    {
        "salary_by_location": [
            {"city": "Madrid", "avg_salary": 65000.50, "employee_count": 245},
            ...
        ]
    }
    """
    try:
        collection = get_mongodb()
        if collection is None:
            return await get_mock_salary_by_location()
        
        # AGREGACIÓN MONGODB: Agrupar por ciudad y calcular salario promedio
        pipeline = [
            {"$match": {
                "location.city": {"$exists": True, "$ne": None},
                "professional.salary": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": "$location.city",
                "avg_salary": {"$avg": "$professional.salary"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avg_salary": -1}},  # Ordenar por salario más alto
            {"$limit": 10}
        ]
        
        result = list(collection.aggregate(pipeline))
        
        return {
            "salary_by_location": [
                {
                    "city": item["_id"],
                    "avg_salary": round(item["avg_salary"], 2),
                    "employee_count": item["count"]
                }
                for item in result
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en salary by location: {e}")
        return await get_mock_salary_by_location()

@api_router.get("/analytics/salary-by-gender")
async def get_salary_by_gender():
    """
    ANÁLISIS DE SUELDOS POR GÉNERO
    Endpoint: GET /api/analytics/salary-by-gender
    
    Para crear gráficos de comparación:
    - Salario promedio por género
    - Brecha salarial
    """
    try:
        collection = get_mongodb()
        if collection is None:
            return await get_mock_salary_by_gender()
        
        pipeline = [
            {"$match": {
                "personal.gender": {"$exists": True, "$ne": None},
                "professional.salary": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": "$personal.gender",
                "avg_salary": {"$avg": "$professional.salary"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avg_salary": -1}}
        ]
        
        result = list(collection.aggregate(pipeline))
        
        return {
            "salary_by_gender": [
                {
                    "gender": item["_id"],
                    "avg_salary": round(item["avg_salary"], 2),
                    "employee_count": item["count"]
                }
                for item in result
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en salary by gender: {e}")
        return await get_mock_salary_by_gender()

@api_router.get("/analytics/salary-by-department")
async def get_salary_by_department():
    """
    ANÁLISIS DE SUELDOS POR DEPARTAMENTO
    Endpoint: GET /api/analytics/salary-by-department
    
    Para crear gráficos detallados:
    - Salario promedio, mínimo y máximo por departamento
    - Distribución salarial
    """
    try:
        collection = get_mongodb()
        if collection is None:
            return await get_mock_salary_by_department()
        
        pipeline = [
            {"$match": {
                "professional.department": {"$exists": True, "$ne": None},
                "professional.salary": {"$exists": True, "$ne": None}
            }},
            {"$group": {
                "_id": "$professional.department",
                "avg_salary": {"$avg": "$professional.salary"},
                "min_salary": {"$min": "$professional.salary"},
                "max_salary": {"$max": "$professional.salary"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avg_salary": -1}},
            {"$limit": 10}
        ]
        
        result = list(collection.aggregate(pipeline))
        
        return {
            "salary_by_department": [
                {
                    "department": item["_id"],
                    "avg_salary": round(item["avg_salary"], 2),
                    "min_salary": round(item["min_salary"], 2),
                    "max_salary": round(item["max_salary"], 2),
                    "employee_count": item["count"]
                }
                for item in result
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error en salary by department: {e}")
        return await get_mock_salary_by_department()

# ========================================
# DATOS MOCK - PARA DESARROLLO Y TESTING
# ========================================

@api_router.get("/mock/stats")
async def get_mock_stats():
    """
    DATOS FALSOS PARA DESARROLLO
    - Se usa cuando MongoDB no está disponible
    - Permite desarrollar el frontend sin depender de la base de datos
    """
    return {
        "total_employees": 1250,
        "avg_salary": 65750.50,
        "top_cities": [
            {"city": "Madrid", "count": 345},
            {"city": "Barcelona", "count": 289},
            {"city": "Valencia", "count": 178},
            {"city": "Sevilla", "count": 134},
            {"city": "Bilbao", "count": 112}
        ],
        "top_departments": [
            {"department": "Tecnología", "count": 285},
            {"department": "Ventas", "count": 245},
            {"department": "Marketing", "count": 189},
            {"department": "RRHH", "count": 156},
            {"department": "Finanzas", "count": 123}
        ],
        "last_updated": datetime.now().isoformat(),
        "status": "success"
    }

async def get_mock_salary_by_location():
    """DATOS MOCK: Sueldos por ubicación"""
    cities = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Zaragoza", "Málaga", "Murcia"]
    
    return {
        "salary_by_location": [
            {
                "city": city,
                "avg_salary": round(random.uniform(50000, 85000), 2),
                "employee_count": random.randint(50, 250)
            }
            for city in cities
        ],
        "timestamp": datetime.now().isoformat()
    }

async def get_mock_salary_by_gender():
    """DATOS MOCK: Sueldos por género"""
    return {
        "salary_by_gender": [
            {"gender": "Male", "avg_salary": 67500.50, "employee_count": 625},
            {"gender": "Female", "avg_salary": 64200.75, "employee_count": 580},
            {"gender": "Other", "avg_salary": 66800.25, "employee_count": 45}
        ],
        "timestamp": datetime.now().isoformat()
    }

async def get_mock_salary_by_department():
    """DATOS MOCK: Sueldos por departamento"""
    departments = [
        {"department": "Tecnología", "avg": 78500, "min": 45000, "max": 120000, "count": 285},
        {"department": "Finanzas", "avg": 72300, "min": 42000, "max": 95000, "count": 123},
        {"department": "Ventas", "avg": 68900, "min": 35000, "max": 85000, "count": 245},
        {"department": "Marketing", "avg": 62500, "min": 38000, "max": 80000, "count": 189},
        {"department": "RRHH", "avg": 58700, "min": 40000, "max": 75000, "count": 156},
        {"department": "Operaciones", "avg": 55200, "min": 32000, "max": 70000, "count": 98}
    ]
    
    return {
        "salary_by_department": [
            {
                "department": dept["department"],
                "avg_salary": float(dept["avg"]),
                "min_salary": float(dept["min"]),
                "max_salary": float(dept["max"]),
                "employee_count": dept["count"]
            }
            for dept in departments
        ],
        "timestamp": datetime.now().isoformat()
    }
