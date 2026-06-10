from __future__ import annotations

import json

from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from app.core.errors import ApiError
from app.routers.process import _do_process
from app.schemas.models import ProcessRequest, ProcessResponse, RecordChunkRequest, RecordCommitRequest
from app.services.record_session import RECORD_SESSION_STORE, SAMPLE_RATE
from app.services.task_store import TASK_STORE

router = APIRouter(prefix="/api/record", tags=["record"])


@router.post("/session")
def create_session() -> dict:
    session = RECORD_SESSION_STORE.create()
    return {"ok": True, "session_id": session.session_id, "sample_rate": SAMPLE_RATE}


@router.delete("/session/{session_id}")
def delete_session(session_id: str) -> dict:
    RECORD_SESSION_STORE.delete(session_id)
    return {"ok": True, "session_id": session_id}


@router.post("/{session_id}/chunk")
def post_chunk(session_id: str, body: RecordChunkRequest) -> dict:
    denoised_b64, latency_ms = RECORD_SESSION_STORE.process_chunk(
        session_id,
        body.seq,
        body.pcm_b64,
        preview_method=body.preview_method,
        preview_strength=body.preview_strength,
    )
    return {"ok": True, "seq": body.seq, "denoised_b64": denoised_b64, "latency_ms": latency_ms}


@router.post("/{session_id}/finish")
def finish_session(session_id: str) -> dict:
    result = RECORD_SESSION_STORE.finish(session_id)
    return {"ok": True, **result}


@router.post("/{session_id}/commit", response_model=ProcessResponse)
def commit_session(session_id: str, body: RecordCommitRequest, background_tasks: BackgroundTasks) -> ProcessResponse:
    settings = body.model_dump()
    created = RECORD_SESSION_STORE.commit(session_id, settings)
    task_id = created["task_id"]
    req = ProcessRequest(task_id=task_id, **{k: v for k, v in settings.items() if k != "task_id"})
    background_tasks.add_task(_do_process, req)
    TASK_STORE.patch(task_id, {"status": "queued", "progress": 0.0, "message": "queued"})
    return ProcessResponse(task_id=task_id, status="queued", message="Task queued from live capture")


@router.get("/{session_id}/audio/raw")
def session_raw_audio(session_id: str) -> FileResponse:
    path = RECORD_SESSION_STORE.audio_path(session_id, "raw")
    return FileResponse(path=path, media_type="audio/wav", filename=path.name)


@router.get("/{session_id}/audio/preview")
def session_preview_audio(session_id: str) -> FileResponse:
    path = RECORD_SESSION_STORE.audio_path(session_id, "preview")
    return FileResponse(path=path, media_type="audio/wav", filename=path.name)


@router.websocket("/{session_id}/stream")
async def record_stream(websocket: WebSocket, session_id: str) -> None:
    await websocket.accept()
    try:
        RECORD_SESSION_STORE.get(session_id)
    except ApiError as exc:
        await websocket.send_json({"type": "error", "code": exc.code, "message": exc.message})
        await websocket.close()
        return

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "code": "bad_json", "message": "Invalid JSON"})
                continue

            if msg.get("type") != "chunk":
                await websocket.send_json({"type": "error", "code": "bad_type", "message": "Expected type chunk"})
                continue

            seq = int(msg.get("seq", -1))
            pcm = msg.get("pcm") or msg.get("pcm_b64") or ""
            preview_method = str(msg.get("preview_method", "omlsa_preview"))
            preview_strength = float(msg.get("preview_strength", 0.8))

            try:
                denoised_b64, latency_ms = RECORD_SESSION_STORE.process_chunk(
                    session_id,
                    seq,
                    pcm,
                    preview_method=preview_method,
                    preview_strength=preview_strength,
                )
                await websocket.send_json(
                    {
                        "type": "denoised",
                        "seq": seq,
                        "pcm": denoised_b64,
                        "latency_ms": latency_ms,
                    }
                )
            except ApiError as exc:
                await websocket.send_json({"type": "error", "code": exc.code, "message": exc.message})
                if exc.code in {"session_not_found", "session_finished", "record_too_long"}:
                    break
    except WebSocketDisconnect:
        return
