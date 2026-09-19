"""Single egress point for model calls, budgets and provider-specific credentials."""
from __future__ import annotations

from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.common.observability import configure_logging

configure_logging()
app = FastAPI(title="LongHorizon Model Gateway", version="v1")


class GenerationRequest(BaseModel):
    experiment_id: str
    run_id: str
    model_alias: str
    input_ref: str = Field(pattern=r"^(s3|file)://")
    max_output_tokens: int = Field(gt=0, le=32768)
    max_cost_usd: float = Field(gt=0)


class GenerationResponse(BaseModel):
    request_id: str
    status: Literal["completed"]
    output_ref: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/generations", response_model=GenerationResponse)
def generate(request: GenerationRequest) -> GenerationResponse:
    """Provider adapters are intentionally injected at deploy time, never into runners."""
    raise HTTPException(501, f"No approved adapter is configured for model alias {request.model_alias}")
