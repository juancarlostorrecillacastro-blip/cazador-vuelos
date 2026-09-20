"""Cliente para la Data API de Travelpayouts: consulta precios de vuelos."""

from dataclasses import dataclass

import requests

PRICES_FOR_DATES_URL = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"


@dataclass
class FlightPrice:
    origin: str
    destination: str
    price: float
    currency: str
    departure_at: str
    airline: str
    transfers: int
    booking_link: str


def find_cheapest_price(
    origin: str, destination: str, currency: str, token: str
) -> FlightPrice | None:
    """Devuelve el vuelo mas barato encontrado para la ruta, o None si no hay resultados."""
    params = {
        "origin": origin,
        "destination": destination,
        "currency": currency,
        "token": token,
        "one_way": "true",
        "sorting": "price",
        "limit": 1,
    }

    response = requests.get(PRICES_FOR_DATES_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()

    if not payload.get("success") or not payload.get("data"):
        return None

    cheapest = payload["data"][0]

    return FlightPrice(
        origin=origin,
        destination=destination,
        price=cheapest["price"],
        currency=currency,
        departure_at=cheapest["departure_at"],
        airline=cheapest["airline"],
        transfers=cheapest["transfers"],
        booking_link="https://www.aviasales.com" + cheapest["link"],
    )
