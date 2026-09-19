"""Machine-readable quality gates for an experiment's evidence, not its outcome."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def assess_quality(summary: dict[str, Any], gates: dict[str, Any]) -> dict[str, Any]:
    groups = summary.get("groups", [])
    checks: list[dict[str, Any]] = []

    def check(name: str, observed: Any, expected: Any, passed: bool) -> None:
        checks.append({"name": name, "observed": observed, "expected": expected, "passed": passed})

    check("minimum_runs", summary.get("runs", 0), gates["minimum_runs"], summary.get("runs", 0) >= gates["minimum_runs"])
    check("minimum_groups", len(groups), gates["minimum_groups"], len(groups) >= gates["minimum_groups"])
    check("runs_per_group", [group.get("n", 0) for group in groups], gates["minimum_runs_per_group"], all(group.get("n", 0) >= gates["minimum_runs_per_group"] for group in groups))
    missing_metrics = sorted({metric for group in groups for metric in gates["required_metrics"] if metric not in group})
    check("required_metrics", missing_metrics, [], not missing_metrics)
    if "expect_simulated" in gates:
        check("simulation_state", summary.get("simulated"), gates["expect_simulated"], summary.get("simulated") == gates["expect_simulated"])
    return {"passed": all(item["passed"] for item in checks), "checks": checks}


def check_files(summary_path: str | Path, gates_path: str | Path) -> dict[str, Any]:
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    gates = json.loads(Path(gates_path).read_text(encoding="utf-8"))
    return assess_quality(summary, gates)


def write_check(result: dict[str, Any], output_path: str | Path) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output
