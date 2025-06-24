# ========================================
# FRONTEND.PY - ROUTER PARA PÁGINAS WEB
# ========================================

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Crear router
router = APIRouter()

# Configurar templates
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Dashboard Principal",
        "active_page": "dashboard"
    })

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Página de analytics avanzados"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "page_title": "Analytics Avanzados",
        "active_page": "analytics"
    })