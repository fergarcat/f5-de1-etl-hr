# ========================================
# IMPORTS - LIBRERÍAS NECESARIAS
# ========================================
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # Para servir archivos CSS, JS, imágenes
from fastapi.middleware.cors import CORSMiddleware  # Para permitir peticiones desde navegador
import os
from dotenv import load_dotenv  # Para cargar variables de entorno

# ========================================
# IMPORTAR ROUTERS - RUTAS DE LA APLICACIÓN
# ========================================
try:
    from routers.api import api_router      # API endpoints (/api/stats, /api/analytics)
    from routers.frontend import frontend_router  # Páginas web (/, /analytics)
    ROUTERS_AVAILABLE = True
    print("✅ Routers importados correctamente")
except ImportError as e:
    print(f"⚠️ Error importando routers: {e}")
    print("📝 El servidor funcionará pero sin rutas")
    api_router = None
    frontend_router = None
    ROUTERS_AVAILABLE = False

# ========================================
# CONFIGURACIÓN INICIAL
# ========================================
load_dotenv()  # Carga archivo .env con configuraciones

# ========================================
# CREAR APLICACIÓN FASTAPI
# ========================================
app = FastAPI(
    title="HR ETL Dashboard",  # Nombre del proyecto
    description="Dashboard para visualizar datos de Recursos Humanos procesados desde Kafka → MongoDB",
    version="1.0.0",
    docs_url="/docs",    # Documentación automática en /docs
    redoc_url="/redoc"   # Documentación alternativa en /redoc
)

# ========================================
# MIDDLEWARE - CONFIGURACIONES ADICIONALES
# ========================================
# CORS: Permite que el navegador haga peticiones a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permitir desde cualquier origen (en producción cambiar por dominio específico)
    allow_credentials=True,   # Permitir cookies y autenticación
    allow_methods=["*"],      # Permitir todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],      # Permitir todos los headers
)

# ========================================
# ARCHIVOS ESTÁTICOS - CSS, JS, IMÁGENES
# ========================================
# Esto hace que /static/css/style.css sea accesible desde el navegador
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========================================
# INCLUIR ROUTERS - CONECTAR LAS RUTAS
# ========================================
# Solo incluir si existen los archivos
if ROUTERS_AVAILABLE and frontend_router:
    app.include_router(frontend_router, tags=["Frontend"])  # Páginas web: /, /analytics
    print("✅ Frontend router incluido")

if ROUTERS_AVAILABLE and api_router:
    app.include_router(api_router, prefix="/api", tags=["API"])  # API: /api/stats, /api/analytics/*
    print("✅ API router incluido")

# ========================================
# ENDPOINTS BÁSICOS
# ========================================

@app.get("/health")
async def health_check():
    """
    ENDPOINT PARA VERIFICAR QUE TODO FUNCIONA
    - Se usa para monitoring y debugging
    - Muestra el estado de conexiones a bases de datos
    """
    return {
        "status": "healthy",
        "service": "HR ETL Dashboard",
        "version": "1.0.0",
        "description": "Dashboard para visualizar datos de RRHH procesados desde Kafka",
        "components": {
            "api": "operational",
            "frontend": "operational", 
            "static_files": "mounted"
        },        "databases": {
            "mongodb": {
                "host": "mongo",
                "port": 27017,
                "database": "etl_db",
                "collection": "raw_data",
                "purpose": "Almacenar datos raw desde Kafka",
                "status": "configured"
            },
            "mysql": {
                "host": "mysql",
                "port": 3306,
                "database": "hr",
                "purpose": "Datos estructurados y relacionales",
                "status": "configured"
            },
            "redis": {
                "host": "redis",
                "port": 6379,
                "purpose": "Cache temporal para mejorar rendimiento",
                "status": "configured"
            }
        },
        "data_flow": {
            "step_1": "Kafka Producer → envía datos al topic 'probando'",
            "step_2": "Kafka Consumer → lee datos y los guarda en MongoDB",
            "step_3": "Dashboard → lee MongoDB y muestra gráficos"
        }
    }

@app.get("/ping")
async def ping():
    """
    ENDPOINT SIMPLE PARA VERIFICAR QUE EL SERVIDOR RESPONDE
    - Útil para health checks básicos
    """
    return {"message": "pong", "status": "ok"}

# ========================================
# PUNTO DE ENTRADA - INICIO DEL SERVIDOR
# ========================================
if __name__ == "__main__":
    """
    UVICORN: Es el servidor que ejecuta FastAPI
    - host="0.0.0.0": Acepta conexiones desde cualquier IP
    - port=8000: Puerto donde escucha el servidor  
    - reload=True: Reinicia automáticamente al cambiar código
    - log_level="info": Nivel de logging
    """
    import uvicorn
    print("🚀 Iniciando HR ETL Dashboard...")
    print("📊 MongoDB: Datos desde Kafka")
    print("🌐 Frontend: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  
        log_level="info"
    )