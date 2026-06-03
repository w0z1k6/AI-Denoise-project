from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.errors import ApiError
from app.services.task_store import TASK_STORE

router = APIRouter(prefix="/api", tags=["result"])


def _task(task_id: str) -> dict:
    try:
        return TASK_STORE.get(task_id)
    except FileNotFoundError:
        raise ApiError("task_not_found", f"Task not found: {task_id}", 404)


def _path_or_404(path_value: str | None, name: str) -> Path:
    if not path_value:
        raise ApiError("result_not_ready", f"{name} is not ready", 409)
    p = Path(path_value)
    if not p.exists():
        raise ApiError("result_missing", f"{name} file missing", 404)
    return p


@router.get("/result/{task_id}/metrics")
def result_metrics(task_id: str) -> dict:
    payload = _task(task_id)
    p = _path_or_404(payload["paths"].get("metrics_json"), "metrics")
    return {"ok": True, "task_id": task_id, "metrics": json.loads(p.read_text(encoding="utf-8"))}


@router.get("/result/{task_id}/plots")
def result_plots(task_id: str) -> dict:
    payload = _task(task_id)
    p = _path_or_404(payload["paths"].get("plots_json"), "plots")
    return {"ok": True, "task_id": task_id, "plots": json.loads(p.read_text(encoding="utf-8"))}


@router.get("/result/{task_id}/audio/original")
def original_audio(task_id: str) -> FileResponse:
    payload = _task(task_id)
    p = _path_or_404(payload["paths"].get("original_wav"), "original")
    return FileResponse(path=p, media_type="audio/wav", filename=p.name)


@router.get("/result/{task_id}/audio/denoised")
def denoised_audio(task_id: str) -> FileResponse:
    payload = _task(task_id)
    p = _path_or_404(payload["paths"].get("denoised_wav"), "denoised")
    return FileResponse(path=p, media_type="audio/wav", filename=p.name)


@router.get("/result/{task_id}/audio/residual")
def residual_audio(task_id: str) -> FileResponse:
    payload = _task(task_id)
    p = _path_or_404(payload["paths"].get("residual_wav"), "residual")
    return FileResponse(path=p, media_type="audio/wav", filename=p.name)

