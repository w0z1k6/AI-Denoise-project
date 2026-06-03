from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import SETTINGS


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStore:
    def __init__(self) -> None:
        self.tasks_dir = (SETTINGS.data_dir / "tasks").resolve()
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

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

    def get(self, task_id: str) -> dict[str, Any]:
        p = self.path(task_id)
        if not p.exists():
            raise FileNotFoundError(f"Task not found: {task_id}")
        return json.loads(p.read_text(encoding="utf-8"))

    def save(self, payload: dict[str, Any]) -> None:
        payload["updated_at"] = _now_iso()
        self.path(payload["task_id"]).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def update(self, task_id: str, **kwargs: Any) -> dict[str, Any]:
        payload = self.get(task_id)
        for k, v in kwargs.items():
            payload[k] = v
        self.save(payload)
        return payload

    def patch(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        payload = self.get(task_id)
        for k, v in updates.items():
            if isinstance(v, dict) and isinstance(payload.get(k), dict):
                payload[k].update(v)
            else:
                payload[k] = v
        self.save(payload)
        return payload

    def list_all(self) -> list[dict[str, Any]]:
        items = []
        for p in sorted(self.tasks_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            items.append(json.loads(p.read_text(encoding="utf-8")))
        return items

    def delete(self, task_id: str) -> None:
        p = self.path(task_id)
        if p.exists():
            p.unlink()


TASK_STORE = TaskStore()

