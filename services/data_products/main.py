from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from longhorizon.nasa_exoplanets import NasaExoplanetClient
from services.common.observability import configure_logging

configure_logging()
app = FastAPI(title="LongHorizon Data Products", version="v1")
client = NasaExoplanetClient()
STATIC = Path(__file__).parent / "static" / "index.html"


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/data-products/nasa-exoplanets")
def nasa_exoplanets() -> dict:
    try:
        return client.snapshot()
    except Exception as exc:
        raise HTTPException(503, "NASA Exoplanet Archive is temporarily unavailable") from exc


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(STATIC)
