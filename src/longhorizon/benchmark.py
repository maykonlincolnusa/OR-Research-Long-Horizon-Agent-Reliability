"""Validation for frozen benchmark task cards and leakage-resistant split policy."""
from __future__ import annotations

import json
import re
import hashlib
from pathlib import Path
from typing import Any

TASK_REQUIRED = {"task_id", "split", "source_instance_id", "repo", "base_commit", "environment_setup_commit", "version", "difficulty", "eval_type", "image_reference", "fail_to_pass_count", "pass_to_pass_count", "problem_statement_sha256", "gold_patch_sha256", "test_patch_sha256", "eval_script_sha256"}
HASH_FIELDS = {"problem_statement_sha256", "gold_patch_sha256", "test_patch_sha256", "eval_script_sha256"}
FORBIDDEN_CONTENT_FIELDS = {"problem_statement", "patch", "test_patch", "eval_script", "hints_text"}


def load_task_cards(path: str | Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def validate_task_cards(tasks: list[dict[str, Any]], splits: dict[str, Any], source: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    ids: set[str] = set()
    split_repos: dict[str, set[str]] = {"development": set(), "holdout": set()}
    for number, task in enumerate(tasks, 1):
        if set(task) != TASK_REQUIRED:
            errors.append(f"task[{number}] does not match the task-card contract")
            continue
        task_id = task["task_id"]
        if task_id in ids:
            errors.append(f"duplicate task_id {task_id}")
        ids.add(task_id)
        if task["split"] not in split_repos:
            errors.append(f"task[{number}] invalid split")
        else:
            split_repos[task["split"]].add(task["repo"])
        if not re.fullmatch(r"[0-9a-f]{40}", task["base_commit"]) or not re.fullmatch(r"[0-9a-f]{40}", task["environment_setup_commit"]):
            errors.append(f"task[{number}] has an invalid git commit")
        if any(not re.fullmatch(r"[0-9a-f]{64}", task[field]) for field in HASH_FIELDS):
            errors.append(f"task[{number}] has an invalid integrity hash")
        if task["fail_to_pass_count"] < 1 or task["pass_to_pass_count"] < 0:
            errors.append(f"task[{number}] has invalid test counts")
        if FORBIDDEN_CONTENT_FIELDS & set(task):
            errors.append(f"task[{number}] exposes evaluator or solution content")
    expected_development, expected_holdout = set(splits.get("development", [])), set(splits.get("holdout", []))
    actual_development = {task["task_id"] for task in tasks if task.get("split") == "development"}
    actual_holdout = {task["task_id"] for task in tasks if task.get("split") == "holdout"}
    if actual_development != expected_development or actual_holdout != expected_holdout:
        errors.append("task cards and split manifest disagree")
    if split_repos["development"] & split_repos["holdout"]:
        errors.append("development and holdout must be repository-disjoint")
    if source.get("task_count") != len(tasks) or not re.fullmatch(r"[0-9a-f]{64}", source.get("source_file_sha256", "")):
        errors.append("source manifest is incomplete or has an invalid hash")
    return errors


def validate_benchmark_files(tasks_path: str | Path, splits_path: str | Path, source_path: str | Path) -> int:
    tasks = load_task_cards(tasks_path)
    errors = validate_task_cards(tasks, json.loads(Path(splits_path).read_text(encoding="utf-8")), json.loads(Path(source_path).read_text(encoding="utf-8")))
    if errors:
        raise ValueError("Invalid benchmark:\n" + "\n".join(errors))
    return len(tasks)


def verify_source_artifact(tasks_path: str | Path, source_path: str | Path, parquet_path: str | Path) -> int:
    """Verify a downloaded source parquet without copying solution-bearing content into this repo."""
    source = json.loads(Path(source_path).read_text(encoding="utf-8"))
    artifact = Path(parquet_path)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != source["source_file_sha256"]:
        raise ValueError("Source parquet SHA-256 does not match the frozen manifest")
    try:
        import pyarrow.parquet as parquet
    except ImportError as exc:
        raise RuntimeError("Install the benchmark extra: pip install .[benchmark]") from exc
    rows = {row["instance_id"]: row for row in parquet.read_table(artifact).to_pylist()}
    verified = 0
    for task in load_task_cards(tasks_path):
        row = rows.get(task["source_instance_id"])
        if row is None:
            raise ValueError(f"Missing source instance {task['source_instance_id']}")
        if row["repo"] != task["repo"] or row["base_commit"] != task["base_commit"] or row["environment_setup_commit"] != task["environment_setup_commit"]:
            raise ValueError(f"Source coordinates differ for {task['task_id']}")
        for source_field, card_field in (("problem_statement", "problem_statement_sha256"), ("patch", "gold_patch_sha256"), ("test_patch", "test_patch_sha256"), ("eval_script", "eval_script_sha256")):
            if hashlib.sha256(row[source_field].encode()).hexdigest() != task[card_field]:
                raise ValueError(f"Source integrity hash differs for {task['task_id']}:{source_field}")
        verified += 1
    return verified
