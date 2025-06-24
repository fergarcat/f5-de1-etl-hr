# ========================================
# MAIN.PY - SERVIDOR FASTAPI HR ETL DASHBOARD
# Sistema ETL completo: Kafka → MongoDB → MySQL → Dashboard Web
# ========================================

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import mysql.connector
import os
import sys
import uvicorn
from pathlib import Path

# Cargar variables de entorno desde la raíz del proyecto
root_dir = Path(__file__).parent.parent
env_path = root_dir / ".env"
load_dotenv(env_path)

# Añadir la raíz al path para importaciones
sys.path.insert(0, str(root_dir))

# Importar routers
from routers.api import router as api_router
from routers.frontend import router as frontend_router

# ========================================
# CREAR APLICACIÓN FASTAPI
# ========================================
app = FastAPI(
    title="HR ETL Dashboard",
    description="Sistema ETL completo para datos de RRHH: Kafka → MongoDB → MySQL → Dashboard Web",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar templates para compatibilidad directa
templates = Jinja2Templates(directory="templates")

# ========================================
# CONFIGURACIÓN DE MYSQL (para health checks directos)
# ========================================
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3307)),
    'user': os.getenv('MYSQL_USER', 'mysql_f5_de1'),
    'password': os.getenv('MYSQL_PASSWORD', '3tL_f542'),
    'database': os.getenv('MYSQL_DATABASE', 'hr')
}

def get_mysql_connection():
    """Obtener conexión directa a MySQL para health checks"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

# ========================================
# CONFIGURAR CORS (para el frontend)
# ========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# MONTAR ARCHIVOS ESTÁTICOS (CSS, JS, imágenes)
# ========================================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========================================
# INCLUIR ROUTERS
# ========================================
app.include_router(api_router)       # API endpoints (/api/*)
app.include_router(frontend_router)  # Páginas web (/, /analytics)

# ========================================
# RUTAS ADICIONALES DIRECTAS (para compatibilidad)
# ========================================
@app.get("/ping")
async def ping():
    """Ping básico para verificar que el servidor responde"""
    return {"message": "pong", "status": "ok"}

# ========================================
# HEALTH CHECK PRINCIPAL CON VERIFICACIÓN DE BD
# ========================================
@app.get("/health")
async def main_health():
    """Health check completo del sistema"""
    
    # Verificar MySQL
    mysql_status = "disconnected"
    try:
        conn = get_mysql_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            mysql_status = "connected"
            conn.close()
    except Exception as e:
        mysql_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "service": "HR ETL Dashboard",
        "version": "3.0.0",
        "description": "Sistema ETL: Kafka → MongoDB → MySQL → Dashboard Web",
        "databases": {
            "mysql": mysql_status
        },
        "endpoints": {
            "dashboard": "http://localhost:8000/",
            "analytics": "http://localhost:8000/analytics", 
            "api_stats": "http://localhost:8000/api/stats",
            "api_employees": "http://localhost:8000/api/employees",
            "api_departments": "http://localhost:8000/api/departments",
            "docs": "http://localhost:8000/docs",
            "health": "http://localhost:8000/health"
        },
        "features": [
            "Dashboard interactivo con gráficos en tiempo real",
            "Analytics avanzados con múltiples visualizaciones", 
            "API RESTful para datos de RRHH",
            "Conexión directa a MySQL con datos fallback",
            "Interfaz responsive con Bootstrap 5",
            "Charts interactivos con Chart.js"
        ]
    }

# ========================================
# FUNCIÓN PRINCIPAL PARA DESARROLLO
# ========================================
if __name__ == "__main__":
    print("🚀 Iniciando HR ETL Dashboard...")
    print("📊 Dashboard: http://localhost:8000")
    print("📈 Analytics: http://localhost:8000/analytics") 
    print("📚 API Docs: http://localhost:8000/docs")
    print("❤️ Health: http://localhost:8000/health")
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )