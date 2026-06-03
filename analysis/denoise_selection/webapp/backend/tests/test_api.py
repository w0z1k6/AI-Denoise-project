from __future__ import annotations

import io

import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _wav_bytes(sr: int = 16000, sec: float = 0.5) -> bytes:
    t = np.linspace(0, sec, int(sr * sec), endpoint=False)
    x = 0.1 * np.sin(2 * np.pi * 220 * t)
    b = io.BytesIO()
    sf.write(b, x.astype(np.float32), sr, format="WAV")
    b.seek(0)
    return b.read()


def test_health() -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["ok"] is True


def test_upload_and_task_status() -> None:
    wav = _wav_bytes()
    res = client.post("/api/upload", files={"file": ("test.wav", wav, "audio/wav")})
    assert res.status_code == 200
    task_id = res.json()["task_id"]

    status = client.get(f"/api/task/{task_id}")
    assert status.status_code == 200
    assert status.json()["status"] in {"uploaded", "queued", "processing", "completed"}

