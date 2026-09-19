"""Benchmark validation and provenance manifests for reproducible experiments."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .types import Task


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_tasks(tasks: list[Task]) -> list[str]:
    errors: list[str] = []
    for task in tasks:
        prefix = f"{task.id}:"
        if not task.id.strip() or not task.repository.strip():
            errors.append(f"{prefix} id and repository must be non-empty")
        if not task.prompt.strip() or not task.acceptance.strip():
            errors.append(f"{prefix} prompt and acceptance must be non-empty")
        if task.horizon < 1:
            errors.append(f"{prefix} horizon must be >= 1")
        if not task.expected_tools:
            errors.append(f"{prefix} expected_tools must be non-empty")
        if len(set(task.expected_tools)) != len(task.expected_tools):
            errors.append(f"{prefix} expected_tools must not contain duplicates")
    return errors


def require_valid_tasks(tasks: list[Task]) -> None:
    errors = validate_tasks(tasks)
    if errors:
        raise ValueError("Invalid benchmark:\n" + "\n".join(errors))


def build_manifest(config_path: str | Path, dataset_path: str | Path, tasks: list[Task], run_count: int | None = None) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "schema_version": "0.1", "harness_version": __version__, "created_at_utc": datetime.now(UTC).isoformat(),
        "config": {"path": str(config_path), "sha256": sha256_file(config_path)},
        "dataset": {"path": str(dataset_path), "sha256": sha256_file(dataset_path), "task_ids": [task.id for task in tasks], "task_count": len(tasks)},
        "runtime": {"python": sys.version.split()[0], "platform": platform.platform()},
    }
    if run_count is not None:
        manifest["run_count"] = run_count
    return manifest


def write_manifest(manifest: dict[str, Any], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return target
