from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


def _bootstrap_interval(values: list[float], draws: int = 1000, seed: int = 7) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(seed)
    samples = sorted(mean(rng.choices(values, k=len(values))) for _ in range(draws))
    return [round(samples[int(draws * 0.025)], 4), round(samples[int(draws * 0.975)], 4)]


def analyze(results_path: str | Path) -> dict[str, Any]:
    records = [json.loads(line) for line in Path(results_path).read_text(encoding="utf-8").splitlines() if line]
    if not records:
        raise ValueError("No run records found")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    fields = ("model", "topology", "memory", "strategy", "context")
    for record in records:
        groups["|".join(record["treatment"][field] for field in fields)].append(record)
    summaries = []
    for _, items in sorted(groups.items()):
        successes, failed = [float(item["task_success"]) for item in items], [item for item in items if item["failure_injected"]]
        summaries.append({
            "treatment": items[0]["treatment"], "n": len(items), "task_success_rate": round(mean(successes), 4),
            "task_success_ci95": _bootstrap_interval(successes), "hallucination_rate": round(sum(item["hallucinations"] for item in items) / len(items), 4),
            "tool_call_accuracy": round(mean(item["tool_call_accuracy"] for item in items), 4),
            "mean_tokens": round(mean(item["input_tokens"] + item["output_tokens"] for item in items), 2),
            "mean_latency_ms": round(mean(item["latency_ms"] for item in items), 2), "mean_cost_usd": round(mean(item["estimated_cost_usd"] for item in items), 6),
            "recovery_rate": round(mean(float(item["recovered_after_failure"]) for item in failed), 4) if failed else None,
        })
    return {"schema_version": "0.1", "simulated": all(item["treatment"]["model"].startswith("fixture-") for item in records), "runs": len(records), "groups": summaries}


def write_summary(results_path: str | Path, output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(analyze(results_path), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output
