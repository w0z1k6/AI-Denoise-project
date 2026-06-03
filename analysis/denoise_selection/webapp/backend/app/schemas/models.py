from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    ok: bool = True
    task_id: str
    filename: str
    status: str


class ProcessRequest(BaseModel):
    task_id: str
    method: str = Field(default="auto")
    run_distill_refine: bool = Field(default=False)
    deepfilter_model_dir: str | None = None
    noisereduce_strength: float = 0.8
    stft_nfft: int = 512
    stft_hop: int = 128


class ProcessResponse(BaseModel):
    ok: bool = True
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    ok: bool = True
    task_id: str
    status: str
    progress: float
    message: str | None = None
    error: str | None = None


class AbxRecordRequest(BaseModel):
    x_is: str
    guess: str


class BookmarkRequest(BaseModel):
    time_sec: float
    note: str

