from __future__ import annotations

from app.services.task_store import TASK_STORE


def add_abx_record(task_id: str, x_is: str, guess: str) -> dict:
    payload = TASK_STORE.get(task_id)
    records = payload.get("abx_records", [])
    rec = {"x_is": x_is, "guess": guess, "correct": x_is == guess}
    records.append(rec)
    payload["abx_records"] = records
    TASK_STORE.save(payload)
    return rec


def abx_stats(task_id: str) -> dict:
    payload = TASK_STORE.get(task_id)
    records = payload.get("abx_records", [])
    total = len(records)
    correct = sum(1 for r in records if r.get("correct"))
    return {"total": total, "correct": correct, "accuracy": (correct / total if total else 0.0)}


def add_bookmark(task_id: str, time_sec: float, note: str) -> dict:
    payload = TASK_STORE.get(task_id)
    bookmarks = payload.get("bookmarks", [])
    bm = {"time_sec": float(time_sec), "note": note}
    bookmarks.append(bm)
    payload["bookmarks"] = bookmarks
    TASK_STORE.save(payload)
    return bm

