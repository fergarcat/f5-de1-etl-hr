#!/usr/bin/env python3
# ========================================
# TEST.PY - HEALTH CHECK BÁSICO DEL SISTEMA
# ========================================

import sys
import os
from datetime import datetime
from pathlib import Path

# Añadir el directorio padre al path para importaciones
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import mysql.connector
    import requests
except ImportError as e:
    print(f"Error importando dependencias: {e}")
    print("Instalar con: pip install mysql-connector-python requests")
    sys.exit(1)

# ========================================
# FUNCIONES DE CONEXIÓN DIRECTAS
# ========================================

def get_mysql_connection():
    """Crear conexión directa a MySQL"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3307)),
            user=os.getenv('MYSQL_USER', 'mysql_f5_de1'),
            password=os.getenv('MYSQL_PASSWORD', '3tL_f542'),
            database=os.getenv('MYSQL_DATABASE', 'hr'),
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

try:
    from kafka_consumer.db_clients.mongo import get_mongodb_connection
except ImportError:
    def get_mongodb_connection():
        print("⚠️ MongoDB connection not available")
        return None

try:
    from kafka_consumer.db_clients.redis import get_redis_connection
except ImportError:
    def get_redis_connection():
        print("⚠️ Redis connection not available")
        return None

async def api_health():
    """Health check de la API y conexiones"""
    health_status = {
        "api": "healthy",
        "timestamp": datetime.now().isoformat(),
        "databases": {}
    }
    
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        health_status["databases"]["mysql"] = "connected"
    except:
        health_status["databases"]["mysql"] = "error"
    
    
    try:
        db = get_mongodb_connection()
        # Test básico de conexión
        db.list_collection_names()
        health_status["databases"]["mongodb"] = "connected"
    except:
        health_status["databases"]["mongodb"] = "error"
    
    # Test Redis
    try:
        r = get_redis_connection()
        r.ping()
        health_status["databases"]["redis"] = "connected"
    except:
        health_status["databases"]["redis"] = "error"
    
    return health_status

def test_mysql_connection():
    """Test básico de conexión MySQL"""
    print("🔍 Probando conexión MySQL...")
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            conn.close()
            print("✅ MySQL: Conexión exitosa")
            return True
        else:
            print("❌ MySQL: No se pudo conectar")
            return False
    except Exception as e:
        print(f"❌ MySQL: Error - {e}")
        return False

def test_api_endpoints():
    """Test básico de endpoints API"""
    print("🔍 Probando endpoints API...")
    try:
        import requests
        
        endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8000/api/stats",
            "http://localhost:8000/api/employees"
        ]
        
        success_count = 0
        for endpoint in endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    print(f"✅ {endpoint}: OK")
                    success_count += 1
                else:
                    print(f"⚠️ {endpoint}: Status {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
        
        return success_count == len(endpoints)
        
    except ImportError:
        print("⚠️ requests no instalado, saltando tests de API")
        return True
    except Exception as e:
        print(f"❌ Error en test de API: {e}")
        return False

def main():
    """Función principal de health check"""
    print("🏥 HEALTH CHECK - SISTEMA HR ETL")
    print("=" * 50)
    
    results = []
    
    # Test MySQL
    mysql_ok = test_mysql_connection()
    results.append(("MySQL", mysql_ok))
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    results.append(("API Endpoints", api_ok))
    
    # Resumen
    print("\n📊 RESUMEN DEL HEALTH CHECK")
    print("-" * 30)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ OK" if success else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if success:
            success_count += 1
    
    print("-" * 30)
    print(f"Total: {success_count}/{len(results)} tests pasaron")
    
    if success_count == len(results):
        print("🎉 ¡Sistema saludable!")
        return 0
    else:
        print("⚠️ Algunos componentes tienen problemas")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)