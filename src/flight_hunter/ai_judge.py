"""Usa la API de Gemini para juzgar, de una vez, que vuelos de una lista son un autentico chollo."""

import json

from google import genai
from google.genai import types

from flight_hunter.api_client import FlightPrice

MODEL = "gemini-2.5-flash"

PROMPT_TEMPLATE = """Eres un experto en precios de vuelos low-cost europeos. Para cada vuelo
de la lista, evalua si es un AUTENTICO CHOLLO (un precio notablemente mas barato de lo habitual
para esa ruta), no simplemente "un vuelo barato cualquiera".

{flights_block}

Responde SOLO con un array JSON de exactamente {count} objetos, en el MISMO ORDEN que la lista,
sin texto alrededor:
[{{"es_chollo": true o false, "razon": "motivo en menos de 15 palabras"}}, ...]"""


def judge_deals(flights: list[FlightPrice], api_key: str) -> list[tuple[bool, str]]:
    """Juzga una lista de vuelos en una sola llamada a la API (evita agotar
    el limite de peticiones por minuto del nivel gratuito de Gemini)."""
    if not flights:
        return []

    client = genai.Client(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(
        flights_block=_build_flights_block(flights),
        count=len(flights),
    )

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0),
    )

    return _parse_batch_verdict(response.text.strip(), expected=len(flights))


def _build_flights_block(flights: list[FlightPrice]) -> str:
    lines = []
    for i, flight in enumerate(flights, start=1):
        escalas = "directo" if flight.transfers == 0 else f"{flight.transfers} escala(s)"
        lines.append(
            f"Vuelo {i}: {flight.origin} -> {flight.destination}, "
            f"{flight.price} {flight.currency} ida/vuelta, {flight.airline}, {escalas}"
        )
    return "\n".join(lines)


def _parse_batch_verdict(text: str, expected: int) -> list[tuple[bool, str]]:
    """Extrae la lista de (es_chollo, razon) de la respuesta de Gemini. Si algo
    no cuadra (JSON invalido o numero de resultados distinto), se trata todo
    como 'no es chollo' para no avisar por error."""
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        results = json.loads(text)
        if not isinstance(results, list) or len(results) != expected:
            raise ValueError("numero de resultados distinto al esperado")
        return [(bool(r.get("es_chollo")), str(r.get("razon", ""))) for r in results]
    except (json.JSONDecodeError, AttributeError, ValueError):
        return [(False, "No se pudo interpretar la respuesta de la IA")] * expected
