from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import SETTINGS
from app.core.errors import api_error_handler
from app.core.logging import setup_logging
from app.routers.abx import router as abx_router
from app.routers.process import router as process_router
from app.routers.result import router as result_router
from app.routers.task import router as task_router
from app.routers.upload import router as upload_router

setup_logging()
app = FastAPI(title=SETTINGS.app_name, version="0.1.0")
app.add_exception_handler(Exception, api_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(process_router)
app.include_router(task_router)
app.include_router(result_router)
app.include_router(abx_router)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "denoise-webapp-backend"}

