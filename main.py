import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from app.database.db import init_db, get_db
from app.api import auth, assessments, questions, results, violations, dashboard, admin, analytics
from app.websocket.manager import manager
from app.services.auth import get_current_user
from app.models.user import User
from app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    logger.info("Database initialized")
    yield

app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Realtime Mock Assessment Examination Platform",
              lifespan=lifespan)

# Global Exception Handler for structured logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "path": request.url.path}
    )

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Register API routers
for router in [auth.router, assessments.router, questions.router,
               results.router, violations.router, dashboard.router, admin.router, analytics.router]:
    app.include_router(router)

# ── Page Routes ──────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/admin-panel", response_class=HTMLResponse)
async def admin_panel_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/exam/{assessment_id}", response_class=HTMLResponse)
async def exam_page(request: Request, assessment_id: int):
    return templates.TemplateResponse("exam.html", {"request": request, "assessment_id": assessment_id})

@app.get("/result/{result_id}", response_class=HTMLResponse)
async def result_page(request: Request, result_id: int):
    return templates.TemplateResponse("result.html", {"request": request, "result_id": result_id})

@app.get("/report/{result_id}", response_class=HTMLResponse)
async def report_page(request: Request, result_id: int):
    return templates.TemplateResponse("report.html", {"request": request, "result_id": result_id})

# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws/exam/{assessment_id}")
async def exam_websocket(websocket: WebSocket, assessment_id: int):
    await manager.connect(websocket, assessment_id)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(assessment_id, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket, assessment_id)
