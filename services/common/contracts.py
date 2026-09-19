from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Budget(BaseModel):
    max_tokens: int = Field(gt=0)
    max_cost_usd: float = Field(gt=0)
    max_wall_time_seconds: int = Field(gt=0)


class ExperimentRequest(BaseModel):
    experiment_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{8,64}$")
    benchmark_version: str = Field(min_length=1)
    treatments: list[dict[str, str]] = Field(min_length=1)
    repetitions: int = Field(ge=1, le=1000)
    seed: int
    budget: Budget


class RunEvent(BaseModel):
    specversion: Literal["1.0"] = "1.0"
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str = Field(pattern=r"^longhorizon\.")
    type: Literal["run.started", "run.progress", "run.completed", "run.failed", "evaluation.completed"]
    subject: str = Field(min_length=1)
    time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any]


def correlation_id(value: str | None) -> str:
    return value if value and len(value) <= 128 else str(uuid4())
