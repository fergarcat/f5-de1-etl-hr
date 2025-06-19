from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

frontend_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@frontend_router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Dashboard principal de DataTech Solutions"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Dashboard Principal",
        "active_page": "dashboard"
    })

@frontend_router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Página de análisis y métricas"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "page_title": "Analytics",
        "active_page": "analytics"
    })

