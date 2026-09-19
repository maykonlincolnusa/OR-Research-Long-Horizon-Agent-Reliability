from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .dataset import load_tasks
from .evaluator import evaluate_fixture
from .fixture_agent import execute_fixture
from .integrity import build_manifest, require_valid_tasks, write_manifest
from .logging import event, write_events
from .types import Treatment

REQUIRED_TREATMENT_KEYS = {"model", "topology", "memory", "strategy", "context"}


def _resolve(config_file: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else config_file.parent.parent / path


def run_experiment(config_path: str | Path) -> tuple[Path, int]:
    config_file = Path(config_path)
    config: dict[str, Any] = json.loads(config_file.read_text(encoding="utf-8"))
    missing = {"dataset", "output", "event_log", "repetitions", "seed", "treatments"} - set(config)
    if missing:
        raise ValueError(f"Config missing: {', '.join(sorted(missing))}")
    dataset = _resolve(config_file, config["dataset"])
    tasks = load_tasks(dataset)
    require_valid_tasks(tasks)
    output, event_log = _resolve(config_file, config["output"]), _resolve(config_file, config["event_log"])
    manifest_path = _resolve(config_file, config.get("manifest", "results/manifest.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    records, log_records = [], []
    for raw in config["treatments"]:
        if set(raw) != REQUIRED_TREATMENT_KEYS:
            raise ValueError(f"Treatment requires exactly {sorted(REQUIRED_TREATMENT_KEYS)}")
        treatment = Treatment(**raw)
        for repetition in range(int(config["repetitions"])):
            for task in tasks:
                record = execute_fixture(task, treatment, int(config["seed"]), repetition)
                evaluation = evaluate_fixture(task, record)
                records.append(record.to_dict())
                log_records.append(event(record.run_id, task.id, 0, "run_started", {"treatment": record.treatment, "seed": record.seed}))
                log_records.extend(event(record.run_id, task.id, index, str(item["kind"]), item) for index, item in enumerate(record.events, 1))
                log_records.append(event(record.run_id, task.id, len(record.events) + 1, "evaluation", evaluation.to_event()))
                log_records.append(event(record.run_id, task.id, len(record.events) + 2, "run_finished", {"task_success": record.task_success, "metrics": {"tool_calls": record.tool_calls, "tokens": record.input_tokens + record.output_tokens, "latency_ms": record.latency_ms}}))
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    write_events(event_log, log_records)
    write_manifest(build_manifest(config_file, dataset, tasks, len(records)), manifest_path)
    return output, len(records)
