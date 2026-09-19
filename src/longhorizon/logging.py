"""Structured, privacy-conscious event logging for research runs."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

SENSITIVE_KEYS = {"api_key", "authorization", "token", "password", "secret", "prompt", "diff", "content"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: "[REDACTED]" if key.lower() in SENSITIVE_KEYS else sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    return value


def event(run_id: str, task_id: str, sequence: int, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(UTC).isoformat(), "run_id": run_id, "task_id": task_id,
        "sequence": sequence, "kind": kind, "payload": sanitize(payload),
    }


def write_events(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
