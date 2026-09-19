from __future__ import annotations

import json
from pathlib import Path

from .types import Task


def load_tasks(path: str | Path) -> list[Task]:
    tasks: list[Task] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    tasks.append(Task(**json.loads(line)))
                except (TypeError, json.JSONDecodeError) as exc:
                    raise ValueError(f"Invalid task at {path}:{line_number}") from exc
    if not tasks:
        raise ValueError(f"Dataset {path} contains no tasks")
    if len({task.id for task in tasks}) != len(tasks):
        raise ValueError("Task ids must be unique")
    return tasks
