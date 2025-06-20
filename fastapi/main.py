from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

# Importar routers
from routers.api import api_router
from routers.frontend import frontend_router

load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(
    title="HR ETL Full Stack Application",
    description="Sistema completo ETL con API y Frontend integrados",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción ser más específico
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos ANTES de las rutas
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir routers
app.include_router(frontend_router, tags=["Frontend"])

# Health check principal
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "HR ETL Full Stack",
        "version": "1.0.0",
        "components": {
            "api": "operational",
            "frontend": "operational",
            "static_files": "mounted"
        }
    }

# Root redirect
@app.get("/ping")
async def ping():
    return {"message": "pong", "status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )