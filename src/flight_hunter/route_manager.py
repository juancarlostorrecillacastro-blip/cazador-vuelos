"""Lee y escribe las rutas de config.yaml a partir de lo que envia el formulario web."""

import re
from pathlib import Path

import yaml

CITY_CODE_PATTERN = re.compile(r"\(([A-Za-z]{3})\)\s*$")
MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")


def extract_iata_code(city_text: str) -> str:
    """Extrae el codigo IATA de un texto tipo 'Madrid (MAD)', tal y como lo
    escribe el usuario al elegir una opcion del desplegable de ciudades."""
    match = CITY_CODE_PATTERN.search(city_text.strip())
    if not match:
        raise ValueError(f"No se reconoce un aeropuerto valido en: {city_text!r}")
    return match.group(1).upper()


def validate_month(month_text: str) -> str:
    """Comprueba que el mes tiene formato YYYY-MM."""
    if not MONTH_PATTERN.match(month_text):
        raise ValueError(f"El mes debe tener formato YYYY-MM, se recibio: {month_text!r}")
    return month_text


def load_routes(config_path: Path) -> list[dict]:
    with open(config_path, encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}
    return data.get("routes", [])


def add_route(config_path: Path, route: dict) -> None:
    data = _load_raw(config_path)
    data.setdefault("routes", []).append(route)
    _save(config_path, data)


def remove_route(config_path: Path, index: int) -> None:
    data = _load_raw(config_path)
    routes = data.get("routes", [])
    if 0 <= index < len(routes):
        routes.pop(index)
    _save(config_path, data)


def _load_raw(config_path: Path) -> dict:
    with open(config_path, encoding="utf-8") as config_file:
        return yaml.safe_load(config_file) or {}


def _save(config_path: Path, data: dict) -> None:
    with open(config_path, "w", encoding="utf-8") as config_file:
        yaml.safe_dump(data, config_file, allow_unicode=True, sort_keys=False)
