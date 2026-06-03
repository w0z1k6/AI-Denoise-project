from __future__ import annotations

from fastapi import APIRouter

from app.schemas.models import AbxRecordRequest, BookmarkRequest
from app.services.abx_service import abx_stats, add_abx_record, add_bookmark

router = APIRouter(prefix="/api", tags=["abx"])


@router.post("/abx/{task_id}/record")
def record_abx(task_id: str, req: AbxRecordRequest) -> dict:
    rec = add_abx_record(task_id, x_is=req.x_is, guess=req.guess)
    return {"ok": True, "record": rec, "stats": abx_stats(task_id)}


@router.get("/abx/{task_id}/stats")
def get_abx_stats(task_id: str) -> dict:
    return {"ok": True, "stats": abx_stats(task_id)}


@router.post("/bookmark/{task_id}")
def add_task_bookmark(task_id: str, req: BookmarkRequest) -> dict:
    return {"ok": True, "bookmark": add_bookmark(task_id, req.time_sec, req.note)}

