"""Telemetry ingestion: contract validation, redaction guard and immutable persistence."""
from __future__ import annotations

import json
import os

import psycopg
from fastapi import FastAPI, HTTPException

from services.common.contracts import RunEvent
from services.common.observability import configure_logging

configure_logging()
DATABASE_URL = os.environ.get("TELEMETRY_DATABASE_URL", "")
SENSITIVE = {"api_key", "authorization", "token", "password", "secret", "prompt", "diff", "content"}
app = FastAPI(title="LongHorizon Telemetry", version="v1")


def _connection() -> psycopg.Connection:
    if not DATABASE_URL:
        raise RuntimeError("TELEMETRY_DATABASE_URL is required")
    return psycopg.connect(DATABASE_URL)


def _has_sensitive_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in SENSITIVE or _has_sensitive_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_has_sensitive_key(item) for item in value)
    return False


@app.on_event("startup")
def migrate() -> None:
    with _connection() as connection, connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS run_events (event_id UUID PRIMARY KEY, experiment_id TEXT NOT NULL, run_id TEXT NOT NULL, event_type TEXT NOT NULL, occurred_at TIMESTAMPTZ NOT NULL, payload JSONB NOT NULL, received_at TIMESTAMPTZ NOT NULL DEFAULT NOW())")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_experiment_run ON run_events(experiment_id, run_id)")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/events", status_code=202)
def ingest(event: RunEvent) -> dict[str, str]:
    if _has_sensitive_key(event.data):
        raise HTTPException(422, "event contains a prohibited sensitive field")
    try:
        with _connection() as connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO run_events (event_id, experiment_id, run_id, event_type, occurred_at, payload) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (event_id) DO NOTHING", (event.id, event.data["experiment_id"], event.subject, event.type, event.time, json.dumps(event.data)))
    except psycopg.Error as exc:
        raise HTTPException(503, "telemetry storage unavailable") from exc
    return {"event_id": event.id, "status": "accepted"}
