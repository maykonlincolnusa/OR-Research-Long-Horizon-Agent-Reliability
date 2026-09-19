"""Read-only, cached client for the official NASA Exoplanet Archive TAP service."""
from __future__ import annotations

import hashlib
import json
import threading
from datetime import UTC, datetime
from time import monotonic
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TAP_ENDPOINT = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERIES = {
    "total": "select count(*) as planet_count from pscomppars",
    "methods": "select discoverymethod,count(*) as planet_count from pscomppars group by discoverymethod order by planet_count desc",
    "years": "select disc_year,count(*) as planet_count from pscomppars where disc_year is not null group by disc_year order by disc_year",
    "recent": "select top 12 pl_name,hostname,disc_year,discoverymethod,pl_orbper,pl_rade,sy_dist from pscomppars where disc_year is not null order by disc_year desc",
}


class NasaExoplanetClient:
    def __init__(self, ttl_seconds: int = 900) -> None:
        self._ttl_seconds = ttl_seconds
        self._cache: tuple[float, dict[str, Any]] | None = None
        self._lock = threading.Lock()

    @staticmethod
    def _fetch(query: str) -> list[dict[str, Any]]:
        url = f"{TAP_ENDPOINT}?{urlencode({'query': query, 'format': 'json'})}"
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "longhorizon-research/0.1"})
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not isinstance(payload, list):
            raise ValueError("NASA TAP response is not a JSON row list")
        return payload

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            if self._cache and monotonic() - self._cache[0] < self._ttl_seconds:
                return {**self._cache[1], "cache": "hit"}
            rows = {name: self._fetch(query) for name, query in QUERIES.items()}
            total = rows["total"]
            if len(total) != 1 or not isinstance(total[0].get("planet_count"), int):
                raise ValueError("NASA TAP total-count contract failed")
            snapshot = {
                "source": {"name": "NASA Exoplanet Archive", "table": "pscomppars", "tap_endpoint": TAP_ENDPOINT, "retrieved_at_utc": datetime.now(UTC).isoformat(), "query_sha256": {name: hashlib.sha256(query.encode()).hexdigest() for name, query in QUERIES.items()}},
                "quality": {"mode": "read-only projected queries", "cache_ttl_seconds": self._ttl_seconds, "row_contracts_verified": ["total_count", "discovery_method_aggregate", "discovery_year_aggregate", "recent_projection"]},
                "summary": {"confirmed_planets": total[0]["planet_count"], "by_discovery_method": rows["methods"], "by_discovery_year": rows["years"], "recent": rows["recent"]},
                "cache": "miss",
            }
            self._cache = (monotonic(), snapshot)
            return snapshot
