from __future__ import annotations

import base64
import shutil
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import numpy as np
import soundfile as sf

from app.config import SETTINGS
from app.core.errors import ApiError
from app.services.denoise_runner import _run_noisereduce
from app.services.file_store import FILE_STORE
from app.services.task_store import TASK_STORE

PROJECT_DENOISE_ROOT = Path(__file__).resolve().parents[4]
if str(PROJECT_DENOISE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_DENOISE_ROOT))

from algorithms import base_omlsa_mcra  # noqa: E402

SAMPLE_RATE = 16000
MAX_DURATION_SEC = 600.0
SESSION_TTL_SEC = 1800.0


def chunk_denoise(pcm: np.ndarray, sr: int, method: str = "omlsa_preview", strength: float = 0.8) -> np.ndarray:
    x = pcm.astype(np.float32)
    if x.size == 0:
        return x
    if method == "noisereduce":
        return _run_noisereduce(x, sr, strength)
    return base_omlsa_mcra(x, sr).astype(np.float32)


def _pcm_b64_to_float32(pcm_b64: str) -> np.ndarray:
    raw = base64.b64decode(pcm_b64)
    ints = np.frombuffer(raw, dtype=np.int16)
    return (ints.astype(np.float32) / 32768.0).astype(np.float32)


def _float32_to_pcm_b64(x: np.ndarray) -> str:
    clipped = np.clip(x, -1.0, 1.0)
    ints = (clipped * 32767.0).astype(np.int16)
    return base64.b64encode(ints.tobytes()).decode("ascii")


@dataclass
class RecordSession:
    session_id: str
    sample_rate: int = SAMPLE_RATE
    created_at: float = field(default_factory=time.time)
    raw_chunks: dict[int, np.ndarray] = field(default_factory=dict)
    denoised_chunks: dict[int, np.ndarray] = field(default_factory=dict)
    next_seq: int = 0
    finished: bool = False
    raw_wav: Path | None = None
    preview_wav: Path | None = None
    duration_sec: float = 0.0
    preview_method: str = "omlsa_preview"
    preview_strength: float = 0.8

    @property
    def dir(self) -> Path:
        return RECORD_SESSION_STORE.base / self.session_id

    @property
    def total_samples(self) -> int:
        if not self.raw_chunks:
            return 0
        ordered = [self.raw_chunks[k] for k in sorted(self.raw_chunks)]
        return int(sum(c.size for c in ordered))


class RecordSessionStore:
    def __init__(self) -> None:
        self.base = (SETTINGS.data_dir / "record_sessions").resolve()
        self.base.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, RecordSession] = {}
        self._lock = threading.Lock()

    def create(self) -> RecordSession:
        session_id = uuid4().hex[:12]
        session = RecordSession(session_id=session_id)
        session.dir.mkdir(parents=True, exist_ok=True)
        with self._lock:
            self._sessions[session_id] = session
        return session

    def get(self, session_id: str) -> RecordSession:
        with self._lock:
            session = self._sessions.get(session_id)
        if not session:
            p = self.base / session_id
            if p.exists():
                raise ApiError("session_finished", "Recording session already closed", 409)
            raise ApiError("session_not_found", f"Session not found: {session_id}", 404)
        if time.time() - session.created_at > SESSION_TTL_SEC:
            self.delete(session_id)
            raise ApiError("session_not_found", f"Session expired: {session_id}", 404)
        return session

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
        p = self.base / session_id
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

    def process_chunk(
        self,
        session_id: str,
        seq: int,
        pcm_b64: str,
        *,
        preview_method: str = "omlsa_preview",
        preview_strength: float = 0.8,
    ) -> tuple[str, int]:
        t0 = time.perf_counter()
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise ApiError("session_not_found", f"Session not found: {session_id}", 404)
            if session.finished:
                raise ApiError("session_finished", "Recording session already finished", 409)
            if seq != session.next_seq:
                raise ApiError("chunk_out_of_order", f"Expected seq {session.next_seq}, got {seq}", 400)

            pcm = _pcm_b64_to_float32(pcm_b64)
            duration = (session.total_samples + pcm.size) / session.sample_rate
            if duration > MAX_DURATION_SEC:
                raise ApiError("record_too_long", "Maximum recording length reached", 400)

            session.preview_method = preview_method
            session.preview_strength = preview_strength
            session.raw_chunks[seq] = pcm
            denoised = chunk_denoise(pcm, session.sample_rate, preview_method, preview_strength)
            session.denoised_chunks[seq] = denoised
            session.next_seq += 1

        latency_ms = int((time.perf_counter() - t0) * 1000)
        return _float32_to_pcm_b64(denoised), latency_ms

    def finish(self, session_id: str) -> dict:
        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                raise ApiError("session_not_found", f"Session not found: {session_id}", 404)
            if session.finished and session.raw_wav and session.preview_wav:
                return {
                    "raw_wav_path": str(session.raw_wav),
                    "preview_wav_path": str(session.preview_wav),
                    "duration_sec": session.duration_sec,
                }

            raw = self._concat_chunks(session.raw_chunks)
            den = self._concat_chunks(session.denoised_chunks)
            if raw.size == 0:
                raise ApiError("empty_recording", "No audio recorded", 400)

            raw_path = session.dir / "raw.wav"
            preview_path = session.dir / "preview_denoised.wav"
            sf.write(raw_path, raw, session.sample_rate)
            sf.write(preview_path, den if den.size else raw, session.sample_rate)

            session.raw_wav = raw_path
            session.preview_wav = preview_path
            session.duration_sec = raw.size / session.sample_rate
            session.finished = True

            return {
                "raw_wav_path": str(raw_path),
                "preview_wav_path": str(preview_path),
                "duration_sec": session.duration_sec,
            }

    def commit(self, session_id: str, settings: dict) -> dict:
        raw_path = self.base / session_id / "raw.wav"
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.raw_wav and session.raw_wav.exists():
                raw_path = session.raw_wav
        if not raw_path.exists():
            raise ApiError("session_not_found", "Finish recording before commit", 409)

        task_id = FILE_STORE.new_task_id()
        dest = FILE_STORE.uploads / f"{task_id}_original.wav"
        shutil.copy2(raw_path, dest)
        TASK_STORE.create(task_id=task_id, filename=f"live_capture_{session_id}.wav", original_wav=str(dest))
        return {"task_id": task_id, "status": "uploaded", "settings": settings}

    @staticmethod
    def _concat_chunks(chunks: dict[int, np.ndarray]) -> np.ndarray:
        if not chunks:
            return np.array([], dtype=np.float32)
        parts = [chunks[k] for k in sorted(chunks)]
        return np.concatenate(parts).astype(np.float32)

    def audio_path(self, session_id: str, kind: str) -> Path:
        session = self.get(session_id)
        if kind == "raw":
            path = session.raw_wav or (session.dir / "raw.wav")
        elif kind == "preview":
            path = session.preview_wav or (session.dir / "preview_denoised.wav")
        else:
            raise ApiError("bad_kind", f"Unknown audio kind: {kind}", 400)
        if not path.exists():
            raise ApiError("result_not_ready", f"{kind} audio is not ready", 409)
        return path


RECORD_SESSION_STORE = RecordSessionStore()
