"""Runner contract. Deploy as an ephemeral job with a sandbox executor implementation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RunJob:
    experiment_id: str
    run_id: str
    task_ref: str
    treatment: dict[str, str]
    max_tokens: int
    max_cost_usd: float
    max_wall_time_seconds: int


class SandboxExecutor(Protocol):
    def execute(self, job: RunJob) -> str:
        """Execute inside an ephemeral workspace and return a private artifact URI."""


def validate_job(job: RunJob) -> None:
    if not job.task_ref.startswith(("s3://", "file://")):
        raise ValueError("runner only accepts immutable artifact references")
    if job.max_tokens <= 0 or job.max_cost_usd <= 0 or job.max_wall_time_seconds <= 0:
        raise ValueError("runner budgets must be positive")
