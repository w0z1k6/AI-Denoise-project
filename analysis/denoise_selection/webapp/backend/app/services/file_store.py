from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from uuid import uuid4

import soundfile as sf
from fastapi import UploadFile

from app.config import SETTINGS
from app.core.errors import ApiError

ALLOWED_EXT = {".wav", ".flac", ".mp3"}


class FileStore:
    def __init__(self) -> None:
        self.base = SETTINGS.data_dir.resolve()
        self.uploads = self.base / "uploads"
        self.processed = self.base / "processed"
        self.plots = self.base / "plots"
        self.tasks = self.base / "tasks"
        for p in (self.uploads, self.processed, self.plots, self.tasks):
            p.mkdir(parents=True, exist_ok=True)

    def new_task_id(self) -> str:
        return uuid4().hex[:12]

    def _safe_name(self, filename: str) -> str:
        return Path(filename).name.replace(" ", "_")

    def save_upload(self, task_id: str, file: UploadFile) -> Path:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in ALLOWED_EXT:
            raise ApiError("bad_file_type", f"Unsupported file extension: {ext}", 400)

        raw_path = self.uploads / f"{task_id}_{self._safe_name(file.filename or 'audio')}"
        with raw_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        return self.to_wav(task_id, raw_path)

    def to_wav(self, task_id: str, raw_path: Path) -> Path:
        out_wav = self.uploads / f"{task_id}_original.wav"
        if raw_path.suffix.lower() == ".wav":
            shutil.copy2(raw_path, out_wav)
            return out_wav
        try:
            x, sr = sf.read(raw_path)
            sf.write(out_wav, x, sr)
            return out_wav
        except Exception:
            cmd = ["ffmpeg", "-y", "-i", str(raw_path), str(out_wav)]
            done = subprocess.run(cmd, check=False, capture_output=True, text=True)
            if done.returncode != 0 or not out_wav.exists():
                raise ApiError("convert_failed", "Failed to convert audio to WAV. Need ffmpeg for this format.", 400)
            return out_wav

    def output_wavs(self, task_id: str) -> tuple[Path, Path]:
        den = self.processed / f"{task_id}_denoised.wav"
        res = self.processed / f"{task_id}_residual.wav"
        return den, res

    def output_jsons(self, task_id: str) -> tuple[Path, Path]:
        metrics = self.plots / f"{task_id}_metrics.json"
        plots = self.plots / f"{task_id}_plots.json"
        return metrics, plots

    def cleanup_task_files(self, task_id: str, task_payload: dict) -> None:
        for key in ("original_wav", "denoised_wav", "residual_wav", "metrics_json", "plots_json"):
            v = task_payload.get("paths", {}).get(key)
            if v:
                p = Path(v)
                if p.exists():
                    p.unlink()
        for p in self.uploads.glob(f"{task_id}_*"):
            if p.exists():
                p.unlink()


FILE_STORE = FileStore()

