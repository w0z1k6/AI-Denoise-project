from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import SETTINGS


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStoreCorruptError(Exception):
    """Task JSON on disk is empty or invalid (often a read-during-write race)."""


class TaskStore:
    def __init__(self) -> None:
        self.tasks_dir = (SETTINGS.data_dir / "tasks").resolve()
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def path(self, task_id: str) -> Path:
        return self.tasks_dir / f"{task_id}.json"

    def create(self, task_id: str, filename: str, original_wav: str) -> dict[str, Any]:
        now = _now_iso()
        payload = {
            "task_id": task_id,
            "filename": filename,
            "status": "uploaded",
            "progress": 0.0,
            "message": "file uploaded",
            "error": None,
            "created_at": now,
            "updated_at": now,
            "settings": {},
            "paths": {
                "original_wav": original_wav,
                "denoised_wav": None,
                "residual_wav": None,
                "metrics_json": None,
                "plots_json": None,
            },
            "abx_records": [],
            "bookmarks": [],
        }
        self.save(payload)
        return payload

    def _read_payload(self, p: Path) -> dict[str, Any]:
        last_err: Exception | None = None
        for attempt in range(5):
            try:
                text = p.read_text(encoding="utf-8").strip()
                if not text:
                    raise json.JSONDecodeError("empty task file", text, 0)
                return json.loads(text)
            except (json.JSONDecodeError, OSError) as exc:
                last_err = exc
                if attempt < 4:
                    time.sleep(0.03 * (attempt + 1))
                    continue
                break
        raise TaskStoreCorruptError(f"Corrupt or unreadable task file: {p}") from last_err

    def get(self, task_id: str) -> dict[str, Any]:
        p = self.path(task_id)
        if not p.exists():
            raise FileNotFoundError(f"Task not found: {task_id}")
        with self._lock:
            return self._read_payload(p)

    def save(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = _now_iso()
        p = self.path(payload["task_id"])
        data = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp = p.with_suffix(".json.tmp")
        with self._lock:
            tmp.write_text(data, encoding="utf-8")
            tmp.replace(p)

    def update(self, task_id: str, **kwargs: Any) -> dict[str, Any]:
        with self._lock:
            payload = self._read_payload(self.path(task_id))
            for k, v in kwargs.items():
                payload[k] = v
            self._save_unlocked(payload)
        return payload

    def patch(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            payload = self._read_payload(self.path(task_id))
            for k, v in updates.items():
                if isinstance(v, dict) and isinstance(payload.get(k), dict):
                    payload[k].update(v)
                else:
                    payload[k] = v
            self._save_unlocked(payload)
        return payload

    def _save_unlocked(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = _now_iso()
        p = self.path(payload["task_id"])
        data = json.dumps(payload, ensure_ascii=False, indent=2)
        tmp = p.with_suffix(".json.tmp")
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(p)

    def list_all(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        with self._lock:
            for p in sorted(self.tasks_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
                try:
                    items.append(self._read_payload(p))
                except TaskStoreCorruptError:
                    continue
        return items

    def delete(self, task_id: str) -> None:
        with self._lock:
            p = self.path(task_id)
            if p.exists():
                p.unlink()
            tmp = p.with_suffix(".json.tmp")
            if tmp.exists():
                tmp.unlink()


TASK_STORE = TaskStore()
