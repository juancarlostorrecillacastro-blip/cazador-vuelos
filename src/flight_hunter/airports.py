"""Traduce codigos IATA de ciudad a nombres legibles, para los avisos."""

import json
from pathlib import Path

CITIES_PATH = Path(__file__).resolve().parent / "data" / "cities.json"

_cities_by_code: dict[str, str] | None = None


def city_name(code: str) -> str:
    """Devuelve el nombre de la ciudad para un codigo IATA, o el propio codigo si no se encuentra."""
    global _cities_by_code
    if _cities_by_code is None:
        _cities_by_code = _load_cities_by_code()
    return _cities_by_code.get(code, code)


def _load_cities_by_code() -> dict[str, str]:
    with open(CITIES_PATH, encoding="utf-8") as cities_file:
        cities = json.load(cities_file)
    return {city["code"]: city["name"] for city in cities}
