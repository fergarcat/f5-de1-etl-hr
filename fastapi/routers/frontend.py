# ========================================
# FRONTEND.PY - PÁGINAS WEB DEL DASHBOARD
# ========================================
"""
Este archivo define las rutas que devuelven páginas HTML
- Página principal (dashboard)
- Página de analytics

FLUJO:
1. Usuario visita http://localhost:8000/
2. Este archivo devuelve index.html
3. El navegador carga CSS y JavaScript
4. JavaScript hace peticiones a /api/* para obtener datos
"""

# ========================================
# IMPORTS NECESARIOS
# ========================================
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# ========================================
# CONFIGURACIÓN
# ========================================
frontend_router = APIRouter()  # Router para agrupar rutas de páginas

# Jinja2: Motor de plantillas para renderizar HTML
templates = Jinja2Templates(directory="templates")

# ========================================
# RUTAS DE PÁGINAS WEB
# ========================================

@frontend_router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """
    PÁGINA PRINCIPAL - DASHBOARD
    Ruta: GET /
    
    Devuelve: templates/index.html
    
    Esta página contiene:
    - Estadísticas generales (total empleados, salario promedio)
    - Gráfico de distribución por ciudades
    - Gráfico de distribución por departamentos
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "HR ETL Dashboard",
        "page": "dashboard"
    })

@frontend_router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """
    PÁGINA DE ANALYTICS - GRÁFICOS AVANZADOS
    Ruta: GET /analytics
    
    Devuelve: templates/analytics.html
    
    Esta página contiene:
    - Análisis de sueldos por ubicación
    - Análisis de sueldos por género
    - Análisis de sueldos por departamento
    - Gráficos más detallados y complejos
    """
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "title": "Analytics - HR ETL Dashboard", 
        "page": "analytics"
    })

# ========================================
# REDIRECCIÓN DE ROOT
# ========================================
# Nota: Este endpoint podría estar duplicado con main.py
# Si hay conflicto, se puede eliminar uno de los dos
@frontend_router.get("/ping")
async def ping():
    """
    ENDPOINT SIMPLE PARA VERIFICAR QUE EL FRONTEND FUNCIONA
    """
    return {"message": "Frontend router funcionando", "status": "ok"}
