from __future__ import annotations

from fastapi import APIRouter

from app.core.errors import ApiError
from app.schemas.models import TaskStatusResponse
from app.services.file_store import FILE_STORE
from app.services.task_store import TASK_STORE

router = APIRouter(prefix="/api", tags=["task"])


@router.get("/task/{task_id}", response_model=TaskStatusResponse)
def task_status(task_id: str) -> TaskStatusResponse:
    try:
        payload = TASK_STORE.get(task_id)
    except FileNotFoundError:
        raise ApiError("task_not_found", f"Task not found: {task_id}", 404)
    return TaskStatusResponse(
        task_id=task_id,
        status=payload["status"],
        progress=float(payload.get("progress", 0.0)),
        message=payload.get("message"),
        error=payload.get("error"),
    )


@router.get("/history")
def history() -> dict:
    items = TASK_STORE.list_all()
    return {"ok": True, "items": items}


@router.delete("/history/{task_id}")
def delete_history(task_id: str) -> dict:
    try:
        payload = TASK_STORE.get(task_id)
    except FileNotFoundError:
        raise ApiError("task_not_found", f"Task not found: {task_id}", 404)
    FILE_STORE.cleanup_task_files(task_id, payload)
    TASK_STORE.delete(task_id)
    return {"ok": True, "task_id": task_id}

