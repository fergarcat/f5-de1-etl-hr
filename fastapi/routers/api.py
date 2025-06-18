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
        
        # Usuarios por ciudad (top 5)
        cursor.execute("""
            SELECT location->>'city' as city, COUNT(*) as count 
            FROM users 
            WHERE location->>'city' IS NOT NULL 
            GROUP BY location->>'city' 
            ORDER BY count DESC 
            LIMIT 5
        """)
        cities_data = [{"city": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        # Usuarios por posición (top 5)
        cursor.execute("""
            SELECT professional->>'position' as position, COUNT(*) as count 
            FROM users 
            WHERE professional->>'position' IS NOT NULL 
            GROUP BY professional->>'position' 
            ORDER BY count DESC 
            LIMIT 5
        """)
        positions_data = [{"position": row[0], "count": row[1]} for row in cursor.fetchall()]
        
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