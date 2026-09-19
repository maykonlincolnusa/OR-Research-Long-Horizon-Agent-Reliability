"""Control plane: durable experiment registration and transactional outbox."""
from __future__ import annotations

import json
import logging
import os
from uuid import uuid4

import psycopg
from fastapi import FastAPI, Header, HTTPException, Response

from services.common.contracts import ExperimentRequest, correlation_id
from services.common.observability import configure_logging

configure_logging()
logger = logging.getLogger("longhorizon.control_plane")
DATABASE_URL = os.environ.get("EXPERIMENT_DATABASE_URL", "")
app = FastAPI(title="LongHorizon Control Plane", version="v1")


def _connection() -> psycopg.Connection:
    if not DATABASE_URL:
        raise RuntimeError("EXPERIMENT_DATABASE_URL is required")
    return psycopg.connect(DATABASE_URL)


@app.on_event("startup")
def migrate() -> None:
    with _connection() as connection, connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS experiments (experiment_id TEXT PRIMARY KEY, request_json JSONB NOT NULL, idempotency_key TEXT UNIQUE NOT NULL, status TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())")
        cursor.execute("CREATE TABLE IF NOT EXISTS outbox (event_id UUID PRIMARY KEY, aggregate_id TEXT NOT NULL, event_type TEXT NOT NULL, payload JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), published_at TIMESTAMPTZ)")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/experiments", status_code=202)
def create_experiment(request: ExperimentRequest, response: Response, idempotency_key: str = Header(min_length=8), x_trace_id: str | None = Header(default=None)) -> dict[str, str]:
    trace_id = correlation_id(x_trace_id)
    payload = request.model_dump(mode="json")
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT experiment_id FROM experiments WHERE idempotency_key = %s", (idempotency_key,))
            existing = cursor.fetchone()
            if existing:
                if existing[0] != request.experiment_id:
                    raise HTTPException(409, "idempotency key belongs to another experiment")
                response.status_code = 200
                return {"experiment_id": request.experiment_id, "status": "accepted", "trace_id": trace_id}
            cursor.execute("INSERT INTO experiments (experiment_id, request_json, idempotency_key, status) VALUES (%s, %s, %s, 'queued')", (request.experiment_id, json.dumps(payload), idempotency_key))
            cursor.execute("INSERT INTO outbox (event_id, aggregate_id, event_type, payload) VALUES (%s, %s, 'experiment.requested.v1', %s)", (str(uuid4()), request.experiment_id, json.dumps({"trace_id": trace_id, "request": payload})))
    except psycopg.Error as exc:
        logger.exception("experiment registration failed", extra={"trace_id": trace_id, "experiment_id": request.experiment_id})
        raise HTTPException(503, "control plane storage unavailable") from exc
    logger.info("experiment accepted", extra={"trace_id": trace_id, "experiment_id": request.experiment_id})
    return {"experiment_id": request.experiment_id, "status": "accepted", "trace_id": trace_id}
