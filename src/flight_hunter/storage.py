"""Guarda en SQLite el mejor precio ya avisado por ruta (origen + destino)."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "deals.db"


@contextmanager
def _connect(db_path: Path):
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS notified_deals (
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                best_price REAL NOT NULL,
                currency TEXT NOT NULL,
                notified_at TEXT NOT NULL,
                PRIMARY KEY (origin, destination)
            )
            """
        )
        yield connection
        connection.commit()
    finally:
        connection.close()


def get_best_notified_price(db_path: Path, origin: str, destination: str) -> float | None:
    """Devuelve el mejor precio ya avisado para esa ruta, o None si nunca se aviso."""
    with _connect(db_path) as connection:
        row = connection.execute(
            "SELECT best_price FROM notified_deals WHERE origin = ? AND destination = ?",
            (origin, destination),
        ).fetchone()
    return row[0] if row else None


def record_notified_price(
    db_path: Path, origin: str, destination: str, price: float, currency: str
) -> None:
    """Guarda (o actualiza) el mejor precio avisado para esa ruta."""
    with _connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO notified_deals (origin, destination, best_price, currency, notified_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (origin, destination) DO UPDATE SET
                best_price = excluded.best_price,
                currency = excluded.currency,
                notified_at = excluded.notified_at
            """,
            (origin, destination, price, currency, datetime.now(timezone.utc).isoformat()),
        )
