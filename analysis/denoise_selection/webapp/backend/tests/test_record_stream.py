from __future__ import annotations

import base64
import io

import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

from app.main import app
from app.services.record_session import chunk_denoise

client = TestClient(app)


def _pcm_b64(samples: np.ndarray) -> str:
    ints = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
    return base64.b64encode(ints.tobytes()).decode("ascii")


def _chunk(sec: float = 0.5, sr: int = 16000) -> str:
    t = np.linspace(0, sec, int(sr * sec), endpoint=False)
    x = 0.2 * np.sin(2 * np.pi * 440 * t) + 0.05 * np.random.randn(t.size)
    return _pcm_b64(x.astype(np.float32))


def test_chunk_denoise_length() -> None:
    sr = 16000
    x = np.random.randn(sr).astype(np.float32) * 0.1
    y = chunk_denoise(x, sr)
    assert y.shape == x.shape


def test_record_session_flow() -> None:
    created = client.post("/api/record/session")
    assert created.status_code == 200
    session_id = created.json()["session_id"]
    assert created.json()["sample_rate"] == 16000

    for seq in range(3):
        res = client.post(
            f"/api/record/{session_id}/chunk",
            json={"seq": seq, "pcm_b64": _chunk()},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["seq"] == seq
        assert body["denoised_b64"]
        assert body["latency_ms"] >= 0

    finished = client.post(f"/api/record/{session_id}/finish")
    assert finished.status_code == 200
    assert finished.json()["duration_sec"] > 0

    raw = client.get(f"/api/record/{session_id}/audio/raw")
    preview = client.get(f"/api/record/{session_id}/audio/preview")
    assert raw.status_code == 200
    assert preview.status_code == 200

    wav = io.BytesIO(raw.content)
    data, sr = sf.read(wav)
    assert sr == 16000
    assert len(data) > 0


def test_record_commit_creates_task() -> None:
    created = client.post("/api/record/session")
    session_id = created.json()["session_id"]
    client.post(f"/api/record/{session_id}/chunk", json={"seq": 0, "pcm_b64": _chunk(0.3)})
    client.post(f"/api/record/{session_id}/finish")

    commit = client.post(
        f"/api/record/{session_id}/commit",
        json={"method": "auto", "run_distill_refine": False, "noisereduce_strength": 0.8},
    )
    assert commit.status_code == 200
    task_id = commit.json()["task_id"]
    assert commit.json()["status"] in {"queued", "processing"}

    status = client.get(f"/api/task/{task_id}")
    assert status.status_code == 200
    assert status.json()["status"] in {"queued", "processing", "completed", "uploaded"}
