"""Carga las credenciales (.env) y la configuracion de busqueda (config.yaml)."""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


@dataclass
class Credentials:
    travelpayouts_token: str
    travelpayouts_marker: str
    telegram_bot_token: str
    telegram_chat_id: str


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {name}. Revisa tu archivo .env")
    return value


def load_credentials() -> Credentials:
    return Credentials(
        travelpayouts_token=_require_env("TRAVELPAYOUTS_TOKEN"),
        travelpayouts_marker=os.environ.get("TRAVELPAYOUTS_MARKER", ""),
        telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_require_env("TELEGRAM_CHAT_ID"),
    )


def load_search_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as config_file:
        return yaml.safe_load(config_file)
