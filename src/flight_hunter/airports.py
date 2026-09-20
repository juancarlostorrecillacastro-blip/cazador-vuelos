"""Carga el listado local de ciudades con aeropuerto, para el formulario web."""

import json
from pathlib import Path

CITIES_PATH = Path(__file__).resolve().parent / "data" / "cities.json"


def load_cities() -> list[dict]:
    """Devuelve la lista de ciudades disponibles: [{'name', 'code', 'country_code'}, ...]."""
    with open(CITIES_PATH, encoding="utf-8") as cities_file:
        return json.load(cities_file)
