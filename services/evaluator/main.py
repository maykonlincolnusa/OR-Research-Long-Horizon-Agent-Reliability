"""Evaluator API: accepts only deterministic evaluator outcomes from isolated jobs."""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from services.common.observability import configure_logging

configure_logging()
app = FastAPI(title="LongHorizon Evaluator", version="v1")


class EvaluationInput(BaseModel):
    experiment_id: str
    run_id: str
    evaluator_version: str
    checks_total: int = Field(ge=1)
    checks_passed: int = Field(ge=0)
    artifact_uri: str = Field(pattern=r"^(s3|file)://")


class EvaluationVerdict(BaseModel):
    experiment_id: str
    run_id: str
    verdict: Literal["passed", "failed"]
    checks_total: int
    checks_passed: int
    evaluator_version: str


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/evaluations", response_model=EvaluationVerdict)
def record_evaluation(payload: EvaluationInput) -> EvaluationVerdict:
    """The sandbox executes tests; this service owns the immutable verdict contract."""
    passed = payload.checks_passed == payload.checks_total
    return EvaluationVerdict(experiment_id=payload.experiment_id, run_id=payload.run_id, verdict="passed" if passed else "failed", checks_total=payload.checks_total, checks_passed=payload.checks_passed, evaluator_version=payload.evaluator_version)
