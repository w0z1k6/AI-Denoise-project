from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.core.errors import ApiError
from app.schemas.models import UploadResponse
from app.services.file_store import FILE_STORE
from app.services.task_store import TASK_STORE

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
def upload_audio(file: UploadFile = File(...)) -> UploadResponse:
    if not file.filename:
        raise ApiError("missing_filename", "Filename is required", 400)
    task_id = FILE_STORE.new_task_id()
    wav_path = FILE_STORE.save_upload(task_id, file)
    TASK_STORE.create(task_id=task_id, filename=file.filename, original_wav=str(wav_path))
    return UploadResponse(task_id=task_id, filename=file.filename, status="uploaded")

