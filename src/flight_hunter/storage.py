"""Guarda en SQLite el mejor precio ya avisado por ruta y mes concreto."""

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
                departure_month TEXT NOT NULL,
                return_month TEXT NOT NULL,
                best_price REAL NOT NULL,
                currency TEXT NOT NULL,
                notified_at TEXT NOT NULL,
                PRIMARY KEY (origin, destination, departure_month, return_month)
            )
            """
        )
        yield connection
        connection.commit()
    finally:
        connection.close()


def _normalize(return_month: str | None) -> str:
    # NULL en SQL no es igual a si mismo (NULL != NULL), lo que rompería el
    # "ON CONFLICT" de la clave primaria. Usamos "" como valor concreto para
    # "sin vuelta" en vez de dejar la columna en NULL.
    return return_month or ""


def get_best_notified_price(
    db_path: Path, origin: str, destination: str, departure_month: str, return_month: str | None = None
) -> float | None:
    """Devuelve el mejor precio ya avisado para esa ruta y mes, o None si nunca se aviso."""
    with _connect(db_path) as connection:
        row = connection.execute(
            """
            SELECT best_price FROM notified_deals
            WHERE origin = ? AND destination = ? AND departure_month = ? AND return_month = ?
            """,
            (origin, destination, departure_month, _normalize(return_month)),
        ).fetchone()
    return row[0] if row else None


def record_notified_price(
    db_path: Path,
    origin: str,
    destination: str,
    departure_month: str,
    return_month: str | None,
    price: float,
    currency: str,
) -> None:
    """Guarda (o actualiza) el mejor precio avisado para esa ruta y mes."""
    with _connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO notified_deals
                (origin, destination, departure_month, return_month, best_price, currency, notified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (origin, destination, departure_month, return_month) DO UPDATE SET
                best_price = excluded.best_price,
                currency = excluded.currency,
                notified_at = excluded.notified_at
            """,
            (
                origin,
                destination,
                departure_month,
                _normalize(return_month),
                price,
                currency,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
