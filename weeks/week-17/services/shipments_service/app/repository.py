import os
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any

ALLOWED_STATUSES = {"created", "in_transit", "delivered", "cancelled"}


class ShipmentRepository:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._lock = threading.Lock()
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        parent = os.path.dirname(self.database_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS shipments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    destination TEXT NOT NULL,
                    tracking TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def create(self, destination: str, tracking: str) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._lock, self._connect() as connection:
            try:
                cursor = connection.execute(
                    """
                    INSERT INTO shipments (destination, tracking, status, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (destination, tracking, "created", created_at),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError(f"tracking already exists: {tracking}") from exc

            shipment_id = int(cursor.lastrowid)
        shipment = self.get(shipment_id)
        if shipment is None:
            raise RuntimeError("created shipment was not persisted")
        return shipment

    def get(self, shipment_id: int) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id, destination, tracking, status, created_at
                FROM shipments
                WHERE id = ?
                """,
                (shipment_id,),
            ).fetchone()
        return dict(row) if row else None

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        normalized_limit = max(1, min(limit or 100, 500))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, destination, tracking, status, created_at
                FROM shipments
                ORDER BY id DESC
                LIMIT ?
                """,
                (normalized_limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def update_status(self, shipment_id: int, status: str) -> dict[str, Any] | None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"unsupported status: {status}")

        with self._lock, self._connect() as connection:
            cursor = connection.execute(
                "UPDATE shipments SET status = ? WHERE id = ?",
                (status, shipment_id),
            )
            if cursor.rowcount == 0:
                return None
        return self.get(shipment_id)
