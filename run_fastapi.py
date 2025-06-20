"""
Script para ejecutar FastAPI desde la raíz del proyecto
"""
import sys
import os
from pathlib import Path

# Agregar la carpeta fastapi al path
current_dir = Path(__file__).parent
fastapi_dir = current_dir / "fastapi"
sys.path.insert(0, str(fastapi_dir))

# Cambiar al directorio fastapi para que los archivos estáticos funcionen
os.chdir(fastapi_dir)

# Importar y ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Iniciando HR ETL Dashboard desde la raíz del proyecto...")
    print("📂 Directorio de trabajo:", os.getcwd())
    print("🌐 URLs disponibles:")
    print("   Frontend:    http://localhost:8000")
    print("   API Docs:    http://localhost:8000/docs")
    print("   Health:      http://localhost:8000/health")
    print("")
    
    # Usar import string para evitar warnings
    uvicorn.run(
        "main:app",  # Import string format
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
