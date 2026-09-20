"""Guarda un historial (JSON) de cada chollo avisado, para consultarlo despues
aunque no se haya visto el aviso de Telegram a tiempo."""

import json
from datetime import datetime, timezone
from pathlib import Path

import requests

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "deal_history.json"
MAX_ENTRIES = 200


def record_deal(history_path: Path, entry: dict) -> None:
    """Añade una entrada al historial, con marca de tiempo, y recorta a
    MAX_ENTRIES para que el archivo no crezca sin limite."""
    entries = load_history(history_path)
    entries.insert(0, {**entry, "notified_at": datetime.now(timezone.utc).isoformat()})
    entries = entries[:MAX_ENTRIES]

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with open(history_path, "w", encoding="utf-8") as history_file:
        json.dump(entries, history_file, ensure_ascii=False, indent=2)


def load_history(history_path: Path) -> list[dict]:
    if not history_path.exists():
        return []
    with open(history_path, encoding="utf-8") as history_file:
        return json.load(history_file)


def fetch_remote_history(repo: str) -> list[dict]:
    """Descarga el historial publicado en GitHub (repo publico, sin credenciales).
    Asi el panel local siempre ve lo ultimo, sin necesitar 'git pull' antes."""
    url = f"https://raw.githubusercontent.com/{repo}/main/data/deal_history.json"
    response = requests.get(url, timeout=10)
    if response.status_code == 404:
        return []
    response.raise_for_status()
    return response.json()
