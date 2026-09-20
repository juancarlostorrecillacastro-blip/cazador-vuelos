"""Usa la API de Claude para juzgar si un precio de vuelo es un autentico chollo."""

import json

import anthropic

MODEL = "claude-haiku-4-5-20251001"

PROMPT_TEMPLATE = """Eres un experto en precios de vuelos low-cost europeos. Evalua si este
vuelo es un AUTENTICO CHOLLO (un precio notablemente mas barato de lo habitual para esa ruta
y duracion), no simplemente "un vuelo barato cualquiera".

Origen: aeropuerto {origin}
Destino: aeropuerto {destination}
Precio: {price} {currency} (ida y vuelta)
Aerolinea: {airline}
Escalas: {transfers}

Responde SOLO con JSON de una linea, sin texto alrededor:
{{"es_chollo": true o false, "razon": "motivo en menos de 15 palabras"}}"""


def is_good_deal(
    origin: str,
    destination: str,
    price: float,
    currency: str,
    airline: str,
    transfers: int,
    api_key: str,
) -> tuple[bool, str]:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = PROMPT_TEMPLATE.format(
        origin=origin,
        destination=destination,
        price=price,
        currency=currency,
        airline=airline,
        transfers=transfers,
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=100,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )

    return _parse_verdict(response.content[0].text.strip())


def _parse_verdict(text: str) -> tuple[bool, str]:
    """Extrae (es_chollo, razon) de la respuesta de Claude. Si no se puede
    interpretar, se trata como 'no es chollo' para no avisar por error."""
    try:
        result = json.loads(text)
        return bool(result.get("es_chollo")), str(result.get("razon", ""))
    except (json.JSONDecodeError, AttributeError):
        return False, "No se pudo interpretar la respuesta de la IA"
