from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

frontend_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@frontend_router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Página principal del dashboard"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "page_title": "Dashboard",
        "active_page": "dashboard"
    })

@frontend_router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request):
    """Página de usuarios"""
    return templates.TemplateResponse("users.html", {
        "request": request,
        "page_title": "Usuarios",
        "active_page": "users"
    })

@frontend_router.get("/realtime", response_class=HTMLResponse)
async def realtime_page(request: Request):
    """Página de tiempo real"""
    return templates.TemplateResponse("realtime.html", {
        "request": request,
        "page_title": "Tiempo Real",
        "active_page": "realtime"
    })

@frontend_router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Página de analytics"""
    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "page_title": "Analytics",
        "active_page": "analytics"
    })