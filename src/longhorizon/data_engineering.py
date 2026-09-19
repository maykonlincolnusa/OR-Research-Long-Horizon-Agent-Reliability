"""Local data-engineering layer: contracts, validation, lineage and SQLite warehouse."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any


TREATMENT_FIELDS = {"model", "topology", "memory", "strategy", "context"}
RUN_REQUIRED = {"run_id", "task_id", "treatment", "seed", "task_success", "hallucinations", "tool_calls", "accurate_tool_calls", "input_tokens", "output_tokens", "latency_ms", "estimated_cost_usd", "failure_injected", "recovered_after_failure", "events"}
EVENT_REQUIRED = {"timestamp_utc", "run_id", "task_id", "sequence", "kind", "payload"}
SENSITIVE_KEYS = {"api_key", "authorization", "token", "password", "secret", "prompt", "diff", "content"}


def _read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at {path}:{line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"Record must be an object at {path}:{line_number}")
        records.append(value)
    return records


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key.lower() in SENSITIVE_KEYS or _contains_sensitive_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_sensitive_key(item) for item in value)
    return False


def validate_run_records(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, record in enumerate(records, 1):
        missing = RUN_REQUIRED - set(record)
        if missing:
            errors.append(f"run[{index}] missing {sorted(missing)}")
            continue
        if not isinstance(record["run_id"], str) or not record["run_id"]:
            errors.append(f"run[{index}] invalid run_id")
        elif record["run_id"] in seen:
            errors.append(f"run[{index}] duplicate run_id {record['run_id']}")
        else:
            seen.add(record["run_id"])
        if set(record["treatment"]) != TREATMENT_FIELDS:
            errors.append(f"run[{index}] invalid treatment dimensions")
        if record["accurate_tool_calls"] > record["tool_calls"]:
            errors.append(f"run[{index}] accurate_tool_calls exceeds tool_calls")
        for field in ("hallucinations", "tool_calls", "accurate_tool_calls", "input_tokens", "output_tokens", "latency_ms"):
            if not isinstance(record[field], int) or record[field] < 0:
                errors.append(f"run[{index}] invalid {field}")
        if not isinstance(record["estimated_cost_usd"], (int, float)) or record["estimated_cost_usd"] < 0:
            errors.append(f"run[{index}] invalid estimated_cost_usd")
    return errors


def validate_events(records: list[dict[str, Any]], known_run_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    sequences: dict[str, list[int]] = defaultdict(list)
    for index, record in enumerate(records, 1):
        missing = EVENT_REQUIRED - set(record)
        if missing:
            errors.append(f"event[{index}] missing {sorted(missing)}")
            continue
        if not isinstance(record["sequence"], int) or record["sequence"] < 0:
            errors.append(f"event[{index}] invalid sequence")
        else:
            sequences[record["run_id"]].append(record["sequence"])
        if known_run_ids is not None and record["run_id"] not in known_run_ids:
            errors.append(f"event[{index}] references unknown run_id")
        if _contains_sensitive_key(record["payload"]):
            errors.append(f"event[{index}] contains sensitive payload key")
    for run_id, values in sequences.items():
        if sorted(values) != list(range(len(values))):
            errors.append(f"events for {run_id} do not have contiguous sequences starting at zero")
    return errors


def validate_artifacts(runs_path: str | Path, events_path: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    runs, events = _read_jsonl(runs_path), _read_jsonl(events_path)
    errors = validate_run_records(runs) + validate_events(events, {record["run_id"] for record in runs})
    if errors:
        raise ValueError("Invalid experiment data:\n" + "\n".join(errors))
    return runs, events


def _experiment_id(manifest: dict[str, Any]) -> str:
    material = f"{manifest['config']['sha256']}:{manifest['dataset']['sha256']}"
    return hashlib.sha256(material.encode()).hexdigest()[:16]


def build_warehouse(runs_path: str | Path, events_path: str | Path, summary_path: str | Path, manifest_path: str | Path, database_path: str | Path) -> tuple[Path, str]:
    runs, events = validate_artifacts(runs_path, events_path)
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    experiment_id, database = _experiment_id(manifest), Path(database_path)
    database.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database) as connection:
        connection.executescript("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE IF NOT EXISTS experiments (experiment_id TEXT PRIMARY KEY, created_at_utc TEXT NOT NULL, config_sha256 TEXT NOT NULL, dataset_sha256 TEXT NOT NULL, manifest_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS runs (experiment_id TEXT NOT NULL, run_id TEXT NOT NULL, task_id TEXT NOT NULL, treatment_json TEXT NOT NULL, seed INTEGER NOT NULL, task_success INTEGER NOT NULL, hallucinations INTEGER NOT NULL, tool_calls INTEGER NOT NULL, accurate_tool_calls INTEGER NOT NULL, input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL, latency_ms INTEGER NOT NULL, estimated_cost_usd REAL NOT NULL, failure_injected INTEGER NOT NULL, recovered_after_failure INTEGER, PRIMARY KEY (experiment_id, run_id), FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id));
            CREATE TABLE IF NOT EXISTS events (experiment_id TEXT NOT NULL, run_id TEXT NOT NULL, sequence INTEGER NOT NULL, timestamp_utc TEXT NOT NULL, task_id TEXT NOT NULL, kind TEXT NOT NULL, payload_json TEXT NOT NULL, PRIMARY KEY (experiment_id, run_id, sequence), FOREIGN KEY (experiment_id, run_id) REFERENCES runs(experiment_id, run_id));
            CREATE TABLE IF NOT EXISTS treatment_kpis (experiment_id TEXT NOT NULL, treatment_key TEXT NOT NULL, n INTEGER NOT NULL, task_success_rate REAL NOT NULL, tool_call_accuracy REAL NOT NULL, hallucination_rate REAL NOT NULL, recovery_rate REAL, mean_tokens REAL NOT NULL, mean_latency_ms REAL NOT NULL, mean_cost_usd REAL NOT NULL, PRIMARY KEY (experiment_id, treatment_key), FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id));
            CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(experiment_id, task_id);
            CREATE INDEX IF NOT EXISTS idx_events_kind ON events(experiment_id, kind);
        """)
        connection.execute("INSERT INTO experiments VALUES (?, ?, ?, ?, ?) ON CONFLICT(experiment_id) DO UPDATE SET created_at_utc=excluded.created_at_utc, config_sha256=excluded.config_sha256, dataset_sha256=excluded.dataset_sha256, manifest_json=excluded.manifest_json", (experiment_id, manifest["created_at_utc"], manifest["config"]["sha256"], manifest["dataset"]["sha256"], json.dumps(manifest, sort_keys=True)))
        connection.executemany("INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            (experiment_id, run["run_id"], run["task_id"], json.dumps(run["treatment"], sort_keys=True), run["seed"], int(run["task_success"]), run["hallucinations"], run["tool_calls"], run["accurate_tool_calls"], run["input_tokens"], run["output_tokens"], run["latency_ms"], run["estimated_cost_usd"], int(run["failure_injected"]), None if run["recovered_after_failure"] is None else int(run["recovered_after_failure"])) for run in runs])
        connection.executemany("INSERT OR REPLACE INTO events VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (experiment_id, item["run_id"], item["sequence"], item["timestamp_utc"], item["task_id"], item["kind"], json.dumps(item["payload"], sort_keys=True)) for item in events])
        connection.executemany("INSERT OR REPLACE INTO treatment_kpis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            (experiment_id, "|".join(group["treatment"][field] for field in ("model", "topology", "memory", "strategy", "context")), group["n"], group["task_success_rate"], group["tool_call_accuracy"], group["hallucination_rate"], group["recovery_rate"], group["mean_tokens"], group["mean_latency_ms"], group["mean_cost_usd"]) for group in summary["groups"]])
    return database, experiment_id
