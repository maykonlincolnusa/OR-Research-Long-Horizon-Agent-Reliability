"""Public baseline report generator with an explicit simulated-results warning."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _treatment_label(treatment: dict[str, str]) -> str:
    fields = ("model", "topology", "memory", "strategy", "context")
    return " / ".join(treatment[field] for field in fields)


def render_markdown(summary: dict[str, Any], quality: dict[str, Any], manifest: dict[str, Any]) -> str:
    status = "PASS" if quality["passed"] else "FAIL"
    warning = "**This is a fixture simulation, not empirical model evidence.**" if summary["simulated"] else "This report contains model-run evidence; audit artifacts before interpretation."
    rows = []
    for group in summary["groups"]:
        rows.append("| " + " | ".join(map(str, (
            _treatment_label(group["treatment"]), group["n"], group["task_success_rate"],
            group["tool_call_accuracy"], group["hallucination_rate"], group["recovery_rate"],
            group["mean_tokens"], group["mean_latency_ms"], group["mean_cost_usd"],
        ))) + " |")
    check_rows = [f"| {item['name']} | {item['observed']} | {item['expected']} | {'pass' if item['passed'] else 'fail'} |" for item in quality["checks"]]
    return f"""# Baseline experiment report

{warning}

## Evidence integrity: {status}

| Check | Observed | Expected | Status |
| --- | --- | --- | --- |
{chr(10).join(check_rows)}

## KPI snapshot

| Treatment | n | Success | Tool accuracy | Hallucinations/run | Recovery | Tokens | Latency ms | Cost USD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Provenance

- Harness: `{manifest['harness_version']}`
- Dataset SHA-256: `{manifest['dataset']['sha256']}`
- Config SHA-256: `{manifest['config']['sha256']}`
- Runs: `{manifest['run_count']}`
- Runtime: Python `{manifest['runtime']['python']}` on `{manifest['runtime']['platform']}`

Interpretation is intentionally withheld: the treatments are not factorially isolated and fixture profiles are synthetic. This report establishes observability and a reproducible baseline only.
"""


def write_report(summary_path: str | Path, quality_path: str | Path, manifest_path: str | Path, output_path: str | Path) -> Path:
    summary = json.loads(Path(summary_path).read_text(encoding="utf-8"))
    quality = json.loads(Path(quality_path).read_text(encoding="utf-8"))
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(summary, quality, manifest), encoding="utf-8")
    return output
