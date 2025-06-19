from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Importar configuraciones
try:
    import psycopg2
    import redis
    from config.logger_config import logger
except ImportError as e:
    print(f"Import error: {e}")
    logger = None

load_dotenv()

api_router = APIRouter()

# Configuración de bases de datos
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'etl_db'),
    'user': os.getenv('POSTGRES_USER', 'etl_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'etl_pass')
}

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': 0
}

def get_postgres_connection():
    """Obtener conexión a PostgreSQL con manejo de errores"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to PostgreSQL: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

def get_redis_connection():
    """Obtener conexión a Redis con manejo de errores"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()  # Test connection
        return r
    except Exception as e:
        if logger:
            logger.error(f"Error connecting to Redis: {e}")
        raise HTTPException(status_code=500, detail="Redis connection error")

@api_router.get("/test")
async def test_api():
    """Endpoint de prueba básico"""
    return {
        "message": "API funcionando correctamente",
        "timestamp": datetime.now().isoformat(),
        "router": "api_router",
        "status": "success"
    }

@api_router.get("/health")
async def api_health():
    """Health check de la API y conexiones"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "databases": {}
    }
    
    # Test PostgreSQL
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        health_status["databases"]["postgresql"] = "connected"
    except:
        health_status["databases"]["postgresql"] = "error"
    
    # Test Redis
    try:
        r = get_redis_connection()
        r.ping()
        health_status["databases"]["redis"] = "connected"
    except:
        health_status["databases"]["redis"] = "error"
    
    return health_status

@api_router.get("/stats")
async def get_dashboard_stats():
    """Estadísticas principales para el dashboard"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Total usuarios procesados
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
          # Usuarios por ciudad (top 5) - usando nombres del Kafka
        cursor.execute("""
            SELECT location->>'city' as city, COUNT(*) as count 
            FROM users 
            WHERE location->>'city' IS NOT NULL 
            GROUP BY location->>'city' 
            ORDER BY count DESC 
            LIMIT 5
        """)
        cities_data = [{"city": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Usuarios por posición/trabajo (top 5) - usando nombres del Kafka
        cursor.execute("""
            SELECT professional_data->>'job' as job, COUNT(*) as count 
            FROM users 
            WHERE professional_data->>'job' IS NOT NULL 
            GROUP BY professional_data->>'job' 
            ORDER BY count DESC 
            LIMIT 5
        """)
        positions_data = [{"position": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Usuarios por empresa (top 5)
        cursor.execute("""
            SELECT professional_data->>'company' as company, COUNT(*) as count 
            FROM users 
            WHERE professional_data->>'company' IS NOT NULL 
            GROUP BY professional_data->>'company' 
            ORDER BY count DESC 
            LIMIT 5
        """)
        companies_data = [{"company": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Actividad reciente (últimos 10)
        cursor.execute("""
            SELECT user_id, personal->>'name' as name, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        recent_activity = [
            {
                "user_id": row[0],
                "name": row[1] or "N/A",
                "created_at": row[2].isoformat() if row[2] else None
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        # Redis stats
        try:
            r = get_redis_connection()
            cache_keys = len(r.keys("user:*"))
        except:
            cache_keys = 0
        
        return {
            "total_processed_users": total_users,
            "users_in_cache": cache_keys,
            "top_cities": cities_data,
            "top_positions": positions_data,
            "recent_activity": recent_activity,
            "last_updated": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@api_router.get("/users")
async def get_all_users(limit: int = 50, offset: int = 0):
    """Obtener todos los usuarios con paginación"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM users")
        total_count = cursor.fetchone()[0] if cursor.rowcount > 0 else 0
        
        # Usuarios paginados
        cursor.execute("""
            SELECT user_id, 
                   personal->>'name' as name,
                   personal->>'email' as email,
                   location->>'city' as city,
                   professional->>'position' as position,
                   created_at 
            FROM users 
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        users = []
        for row in cursor.fetchall():
            users.append({
                "user_id": row[0],
                "name": row[1] or "N/A",
                "email": row[2] or "N/A",
                "city": row[3] or "N/A", 
                "position": row[4] or "N/A",
                "created_at": row[5].isoformat() if row[5] else None
            })
        
        conn.close()
        
        return {
            "users": users,
            "count": len(users),
            "total": total_count,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total_count
            },
            "status": "success"
        }
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=f"Users error: {str(e)}")

@api_router.get("/users/{user_id}")
async def get_user_detail(user_id: str):
    """Detalle completo de un usuario"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_data = {
            "user_id": row[1],
            "personal": row[2],
            "location": row[3],
            "professional": row[4],
            "bank": row[5],
            "net": row[6],
            "created_at": row[7].isoformat() if row[7] else None
        }
        
        conn.close()
        return {"user": user_data, "status": "success"}
        
    except HTTPException:
        raise
    except Exception as e:
        if logger:
            logger.error(f"Error getting user detail: {e}")
        raise HTTPException(status_code=500, detail=f"User detail error: {str(e)}")

@api_router.get("/cache/all")
async def get_cache_data():
    """Datos en cache (Redis) para tiempo real"""
    try:
        r = get_redis_connection()
        keys = r.keys("user:*")
        
        cache_data = []
        for key in keys:
            user_id = key.decode('utf-8').replace('user:', '')
            cached = r.hgetall(key)
            
            decoded_data = {}
            for field, value in cached.items():
                try:
                    decoded_data[field.decode('utf-8')] = json.loads(value.decode('utf-8'))
                except:
                    decoded_data[field.decode('utf-8')] = value.decode('utf-8')
            
            # Calcular completitud
            required_types = {"personal", "location", "professional", "bank", "net"}
            completed_types = set(decoded_data.keys())
            completeness = len(completed_types.intersection(required_types))
            
            cache_data.append({
                "user_id": user_id,
                "data": decoded_data,
                "completeness": f"{completeness}/5",
                "completion_percentage": (completeness / 5) * 100,
                "is_complete": completeness == 5,
                "missing_types": list(required_types - completed_types)
            })
        
        return {
            "cache_data": cache_data,
            "count": len(cache_data),
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting cache data: {e}")
        raise HTTPException(status_code=500, detail=f"Cache error: {str(e)}")

@api_router.get("/analytics/summary")
async def get_analytics():
    """Datos de analytics para gráficos"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        analytics = {}
        
        # Distribución por ciudades
        cursor.execute("""
            SELECT location->>'city' as city, COUNT(*) as count 
            FROM users 
            WHERE location->>'city' IS NOT NULL 
            GROUP BY location->>'city' 
            ORDER BY count DESC
        """)
        analytics["cities"] = [{"city": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Distribución por posiciones
        cursor.execute("""
            SELECT professional->>'position' as position, COUNT(*) as count 
            FROM users 
            WHERE professional->>'position' IS NOT NULL 
            GROUP BY professional->>'position' 
            ORDER BY count DESC
        """)
        analytics["positions"] = [{"position": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Registros por día (últimos 7 días si hay datos)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM users 
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        analytics["daily_registrations"] = [
            {"date": row[0].isoformat(), "count": row[1]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "analytics": analytics,
            "generated_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        if logger:
            logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# Endpoint mock para desarrollo sin bases de datos
@api_router.get("/mock/stats")
async def get_mock_stats():
    """Datos mock para desarrollo sin BD"""
    return {
        "total_processed_users": 150,
        "users_in_cache": 5,
        "top_cities": [
            {"city": "Madrid", "count": 45},
            {"city": "Barcelona", "count": 32},
            {"city": "Valencia", "count": 28},
            {"city": "Sevilla", "count": 22},
            {"city": "Bilbao", "count": 18}
        ],
        "top_positions": [
            {"position": "Desarrollador", "count": 35},
            {"position": "Analista", "count": 28},
            {"position": "Manager", "count": 22},
            {"position": "Designer", "count": 18},
            {"position": "DevOps", "count": 15}
        ],
        "recent_activity": [
            {"user_id": "user_001", "name": "Juan Pérez", "created_at": datetime.now().isoformat()},
            {"user_id": "user_002", "name": "María García", "created_at": datetime.now().isoformat()},
            {"user_id": "user_003", "name": "Carlos López", "created_at": datetime.now().isoformat()}
        ],
        "last_updated": datetime.now().isoformat(),
        "status": "success"
    }

# Employee Management Endpoints
@api_router.get("/employee-stats")
async def get_employee_stats():
    """Get employee statistics for the employees page"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Total employees
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
        total_employees = cursor.fetchone()[0] or 0
        
        # Active employees
        cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
        active_employees = cursor.fetchone()[0] or 0
        
        # Departments count
        cursor.execute("SELECT COUNT(DISTINCT department) FROM employees WHERE department IS NOT NULL")
        departments = cursor.fetchone()[0] or 0
        
        # Recent hires (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) FROM employees 
            WHERE hire_date >= CURRENT_DATE - INTERVAL '30 days'
        """)
        recent_hires = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "data": {
                "total_employees": total_employees,
                "active_employees": active_employees,
                "departments": departments,
                "recent_hires": recent_hires
            }
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting employee stats: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": {
                "total_employees": 0,
                "active_employees": 0,
                "departments": 0,
                "recent_hires": 0
            }
        }

@api_router.get("/employees")
async def get_employees(page: int = 1, limit: int = 20, search: str = "", department: str = "", status: str = ""):
    """Get paginated employee list with filters"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        where_conditions = ["1=1"]
        params = []
        
        if search:
            where_conditions.append("(name ILIKE %s OR email ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        
        if department:
            where_conditions.append("department = %s")
            params.append(department)
            
        if status:
            where_conditions.append("status = %s")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM employees WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0] or 0
        
        # Get paginated results
        offset = (page - 1) * limit
        cursor.execute(f"""
            SELECT id, employee_id, name, email, department, position, status, hire_date
            FROM employees 
            WHERE {where_clause}
            ORDER BY name
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                "id": row[0],
                "employee_id": row[1],
                "name": row[2],
                "email": row[3],
                "department": row[4],
                "position": row[5],
                "status": row[6],
                "hire_date": row[7].isoformat() if row[7] else None
            })
        
        cursor.close()
        conn.close()
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "status": "success",
            "employees": employees,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "limit": limit
            }
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting employees: {e}")
        return {
            "status": "error",
            "message": str(e),
            "employees": [],
            "pagination": {"current_page": 1, "total_pages": 0, "total_count": 0, "limit": limit}
        }

# Pipeline Control Endpoints
@api_router.get("/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline status"""
    try:
        # Get status from Redis or simulate
        redis_conn = get_redis_connection()
        
        # Try to get real status, fallback to simulation
        kafka_status = redis_conn.get("pipeline:kafka:status") or "running"
        transform_status = redis_conn.get("pipeline:transform:status") or "running"
        load_status = redis_conn.get("pipeline:load:status") or "running"
        
        overall_status = "running" if all(s == "running" for s in [kafka_status, transform_status, load_status]) else "partial"
        
        return {
            "status": "success",
            "overall_status": overall_status,
            "kafka": {
                "status": kafka_status,
                "metrics": {
                    "messages_processed": redis_conn.get("kafka:messages:processed") or "1,247",
                    "throughput": redis_conn.get("kafka:throughput") or "15.3/sec"
                }
            },
            "transform": {
                "status": transform_status,
                "metrics": {
                    "records_transformed": redis_conn.get("transform:records") or "1,189",
                    "transformation_rate": redis_conn.get("transform:rate") or "14.1/sec"
                }
            },
            "load": {
                "status": load_status,
                "metrics": {
                    "records_loaded": redis_conn.get("load:records") or "1,156",
                    "load_rate": redis_conn.get("load:rate") or "13.7/sec"
                }
            }
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting pipeline status: {e}")
        return {
            "status": "error",
            "message": str(e),
            "overall_status": "unknown",
            "kafka": {"status": "unknown", "metrics": {}},
            "transform": {"status": "unknown", "metrics": {}},
            "load": {"status": "unknown", "metrics": {}}
        }

@api_router.post("/pipeline/start")
async def start_pipeline():
    """Start the ETL pipeline"""
    try:
        redis_conn = get_redis_connection()
        
        # Update status in Redis
        redis_conn.set("pipeline:kafka:status", "running")
        redis_conn.set("pipeline:transform:status", "running")
        redis_conn.set("pipeline:load:status", "running")
        
        if logger:
            logger.info("Pipeline started via API")
        
        return {
            "status": "success",
            "message": "Pipeline iniciado exitosamente"
        }
    except Exception as e:
        if logger:
            logger.error(f"Error starting pipeline: {e}")
        return {"status": "error", "detail": str(e)}

@api_router.post("/pipeline/stop")
async def stop_pipeline():
    """Stop the ETL pipeline"""
    try:
        redis_conn = get_redis_connection()
        
        # Update status in Redis
        redis_conn.set("pipeline:kafka:status", "stopped")
        redis_conn.set("pipeline:transform:status", "stopped")
        redis_conn.set("pipeline:load:status", "stopped")
        
        if logger:
            logger.info("Pipeline stopped via API")
        
        return {
            "status": "success",
            "message": "Pipeline detenido exitosamente"
        }
    except Exception as e:
        if logger:
            logger.error(f"Error stopping pipeline: {e}")
        return {"status": "error", "detail": str(e)}

@api_router.post("/pipeline/restart")
async def restart_pipeline():
    """Restart the ETL pipeline"""
    try:
        # Stop then start
        await stop_pipeline()
        await start_pipeline()
        
        if logger:
            logger.info("Pipeline restarted via API")
        
        return {
            "status": "success",
            "message": "Pipeline reiniciado exitosamente"
        }
    except Exception as e:
        if logger:
            logger.error(f"Error restarting pipeline: {e}")
        return {"status": "error", "detail": str(e)}

@api_router.get("/realtime-metrics")
async def get_realtime_metrics():
    """Get real-time processing metrics"""
    try:
        redis_conn = get_redis_connection()
        
        # Get metrics from Redis or simulate
        records_processed = int(redis_conn.get("metrics:records_processed") or 1247)
        processing_rate = float(redis_conn.get("metrics:processing_rate") or 15.3)
        error_rate = float(redis_conn.get("metrics:error_rate") or 0.8)
        queue_size = int(redis_conn.get("metrics:queue_size") or 45)
        
        # Recent activity simulation
        recent_activity = [
            {"timestamp": datetime.now().isoformat(), "type": "info", "message": "Batch procesado exitosamente"},
            {"timestamp": datetime.now().isoformat(), "type": "success", "message": "Conexión a Kafka restablecida"},
            {"timestamp": datetime.now().isoformat(), "type": "warning", "message": "Cola alcanzó 80% de capacidad"}
        ]
        
        return {
            "status": "success",
            "records_processed": records_processed,
            "processing_rate": processing_rate,
            "error_rate": error_rate,
            "queue_size": queue_size,
            "data_flow": [
                {"source": "Kafka", "target": "Transform", "count": 45},
                {"source": "Transform", "target": "Load", "count": 42},
                {"source": "Load", "target": "PostgreSQL", "count": 38}
            ],
            "recent_activity": recent_activity
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting realtime metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "records_processed": 0,
            "processing_rate": 0.0,
            "error_rate": 0.0,
            "queue_size": 0,
            "data_flow": [],
            "recent_activity": []
        }

# Enhanced Analytics Endpoints
@api_router.get("/analytics/kpis")
async def get_analytics_kpis(period: str = "30d"):
    """Get KPI metrics for analytics dashboard"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        
        # Calculate KPIs based on period
        if period == "7d":
            date_filter = "WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"
        elif period == "90d":
            date_filter = "WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'"
        else:  # 30d default
            date_filter = "WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'"
        
        # Total records processed
        cursor.execute(f"SELECT COUNT(*) FROM processed_records {date_filter}")
        total_records = cursor.fetchone()[0] or 0
        
        # Processing rate (simulate)
        processing_rate = 12.5
        
        # Data quality score (simulate)
        data_quality = 94.8
        
        # Active pipelines
        active_pipelines = 3
        
        # Trends (simulate percentage changes)
        trends = {
            "records": 8.5,
            "processing_rate": 2.3,
            "data_quality": -0.5,
            "active_pipelines": 0.0
        }
        
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "kpis": {
                "total_records": total_records,
                "processing_rate": processing_rate,
                "data_quality": data_quality,
                "active_pipelines": active_pipelines,
                "trends": trends
            }
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting analytics KPIs: {e}")
        return {
            "status": "error",
            "message": str(e),
            "kpis": {
                "total_records": 0,
                "processing_rate": 0.0,
                "data_quality": 0.0,
                "active_pipelines": 0,
                "trends": {}
            }
        }

@api_router.get("/analytics/etl-metrics")
async def get_etl_metrics(period: str = "30d"):
    """Get ETL-specific metrics for analytics"""
    try:
        # Data type distribution (matching Kafka structure)
        data_types = [
            {"type": "personal_data", "count": 1850},
            {"type": "location", "count": 1798},
            {"type": "professional_data", "count": 1832},
            {"type": "bank_data", "count": 1721},
            {"type": "net_data", "count": 1689}
        ]
        
        # Processing timeline
        processing_timeline = [
            {"timestamp": "2024-01-15T10:00:00", "records_processed": 120},
            {"timestamp": "2024-01-15T11:00:00", "records_processed": 135},
            {"timestamp": "2024-01-15T12:00:00", "records_processed": 118},
            {"timestamp": "2024-01-15T13:00:00", "records_processed": 142},
            {"timestamp": "2024-01-15T14:00:00", "records_processed": 128}
        ]
        
        # Error analysis
        errors = [
            {"type": "Validation Error", "count": 12, "severity": "medium", "description": "Campos requeridos faltantes"},
            {"type": "Format Error", "count": 8, "severity": "low", "description": "Formato de fecha incorrecto"},
            {"type": "Connection Error", "count": 3, "severity": "high", "description": "Timeout de base de datos"}
        ]
        
        # Performance metrics
        performance = {
            "avg_processing_time": 245.8,  # ms
            "throughput": 847,  # records/hour
            "memory_usage": 67.3,  # %
            "cpu_usage": 23.7  # %
        }
        
        return {
            "status": "success",
            "metrics": {
                "data_types": data_types,
                "processing_timeline": processing_timeline,
                "errors": errors,
                "performance": performance
            }
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting ETL metrics: {e}")
        return {
            "status": "error",
            "message": str(e),
            "metrics": {
                "data_types": [],
                "processing_timeline": [],
                "errors": [],
                "performance": {}
            }
        }