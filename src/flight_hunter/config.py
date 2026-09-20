"""Carga las credenciales desde el .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Credentials:
    travelpayouts_token: str
    telegram_bot_token: str
    telegram_chat_id: str
    gemini_api_key: str
    rapidapi_key: str
    rapidapi_host: str


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Falta la variable de entorno {name}. Revisa tu archivo .env")
    return value


def load_credentials() -> Credentials:
    return Credentials(
        travelpayouts_token=_require_env("TRAVELPAYOUTS_TOKEN"),
        telegram_bot_token=_require_env("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=_require_env("TELEGRAM_CHAT_ID"),
        gemini_api_key=_require_env("GEMINI_API_KEY"),
        rapidapi_key=os.environ.get("RAPIDAPI_KEY", ""),
        rapidapi_host=os.environ.get("RAPIDAPI_HOST", ""),
    )
