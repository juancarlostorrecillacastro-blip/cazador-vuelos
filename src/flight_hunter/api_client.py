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
    return_at: str | None
    airline: str
    transfers: int
    return_transfers: int | None
    booking_link: str


def find_cheapest_price(
    origin: str,
    destination: str,
    currency: str,
    token: str,
    departure_month: str,
    return_month: str | None = None,
) -> FlightPrice | None:
    """Devuelve el vuelo mas barato del mes indicado, o None si no hay resultados.

    departure_month y return_month usan formato "YYYY-MM": la API busca el precio
    mas barato en todo ese mes, no en una fecha exacta. Si return_month se omite,
    la busqueda es solo de ida.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "currency": currency,
        "token": token,
        "departure_at": departure_month,
        "sorting": "price",
        "limit": 1,
    }
    if return_month:
        params["return_at"] = return_month
        params["one_way"] = "false"
    else:
        params["one_way"] = "true"

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
        return_at=cheapest.get("return_at"),
        airline=cheapest["airline"],
        transfers=cheapest["transfers"],
        return_transfers=cheapest.get("return_transfers"),
        booking_link="https://www.aviasales.com" + cheapest["link"],
    )
