import json
import os
import sqlite3
import threading
from typing import Any

from fastapi import FastAPI, status
from pydantic import BaseModel, Field

from app.settings import get_settings

settings = get_settings()
lock = threading.Lock()


class ShipmentEventIn(BaseModel):
    type: str = Field(..., min_length=3, max_length=80)
    shipment: dict[str, Any]
    emitted_at: str


def _connect() -> sqlite3.Connection:
    parent = os.path.dirname(settings.database_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def _init_schema() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                shipment TEXT NOT NULL,
                emitted_at TEXT NOT NULL
            )
            """
        )


_init_schema()
app = FastAPI(title="shipments-s13 audit service", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "project_code": settings.project_code,
        "service": settings.service_name,
    }


@app.post("/internal/events", status_code=status.HTTP_202_ACCEPTED)
def accept_event(event: ShipmentEventIn) -> dict[str, int | str]:
    with lock, _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO audit_events (type, shipment, emitted_at)
            VALUES (?, ?, ?)
            """,
            (event.type, json.dumps(event.shipment, sort_keys=True), event.emitted_at),
        )
        event_id = int(cursor.lastrowid)
    return {"status": "accepted", "id": event_id}


@app.get("/events")
def list_events(limit: int = 100) -> list[dict[str, Any]]:
    normalized_limit = max(1, min(limit or 100, 500))
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, type, shipment, emitted_at
            FROM audit_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (normalized_limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "type": row["type"],
            "shipment": json.loads(row["shipment"]),
            "emitted_at": row["emitted_at"],
        }
        for row in rows
    ]
