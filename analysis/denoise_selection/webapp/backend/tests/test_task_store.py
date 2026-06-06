from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.services import task_store as task_store_mod


@pytest.fixture()
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(task_store_mod.SETTINGS, "data_dir", tmp_path)
    return task_store_mod.TaskStore()


def test_atomic_save_survives_concurrent_read(store: task_store_mod.TaskStore) -> None:
    payload = store.create("abc123", "test.wav", "/tmp/test.wav")
    p = store.path("abc123")

    for i in range(20):
        payload["progress"] = i / 20
        payload["message"] = f"step {i}"
        store.save(payload)
        loaded = store.get("abc123")
        assert loaded["task_id"] == "abc123"
        assert json.loads(p.read_text(encoding="utf-8"))["task_id"] == "abc123"


def test_patch_updates_nested_settings(store: task_store_mod.TaskStore) -> None:
    store.create("t1", "a.wav", "/tmp/a.wav")
    store.patch("t1", {"settings": {"method": "deepfilter"}})
    got = store.get("t1")
    assert got["settings"]["method"] == "deepfilter"
