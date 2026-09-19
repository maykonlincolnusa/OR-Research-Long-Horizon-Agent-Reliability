"""Transactional-outbox relay; publish after commit, never from the request transaction."""
from __future__ import annotations

import asyncio
import json
import os

import nats
import psycopg

DATABASE_URL = os.environ["EXPERIMENT_DATABASE_URL"]
NATS_URL = os.environ["NATS_URL"]


async def relay() -> None:
    client = await nats.connect(NATS_URL)
    while True:
        with psycopg.connect(DATABASE_URL) as connection, connection.cursor() as cursor:
            cursor.execute("SELECT event_id, event_type, payload FROM outbox WHERE published_at IS NULL ORDER BY created_at FOR UPDATE SKIP LOCKED LIMIT 50")
            pending = cursor.fetchall()
            for event_id, event_type, payload in pending:
                await client.publish(event_type, json.dumps(payload).encode())
                cursor.execute("UPDATE outbox SET published_at = NOW() WHERE event_id = %s", (event_id,))
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(relay())
