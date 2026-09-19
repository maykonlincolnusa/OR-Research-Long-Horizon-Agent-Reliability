"""Evaluator boundary: replace this module, not the harness, for real repositories."""
from __future__ import annotations

from dataclasses import dataclass

from .types import RunRecord, Task


@dataclass(frozen=True)
class Evaluation:
    evaluator: str
    task_success: bool
    tool_contract_violations: int
    acceptance: str

    def to_event(self) -> dict[str, object]:
        return {
            "kind": "evaluation", "evaluator": self.evaluator, "task_success": self.task_success,
            "tool_contract_violations": self.tool_contract_violations, "acceptance": self.acceptance,
        }


def evaluate_fixture(task: Task, record: RunRecord) -> Evaluation:
    """Checks the run-record contract; real benchmarks should run isolated tests here."""
    violations = max(0, len(task.expected_tools) - record.accurate_tool_calls)
    return Evaluation(
        evaluator="fixture-contract-v1", task_success=record.task_success,
        tool_contract_violations=violations, acceptance=task.acceptance,
    )
