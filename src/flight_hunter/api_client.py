"""Cliente para la Data API de Travelpayouts: precios mas baratos a cualquier destino."""

from dataclasses import dataclass
from datetime import datetime

import requests

CHEAP_DESTINATIONS_URL = "https://api.travelpayouts.com/v1/prices/cheap"
MIN_TRIP_NIGHTS = 4  # ida y vuelta el mismo dia (o casi) no es un viaje real


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
    booking_link: str


def find_cheap_destinations(
    origin: str, currency: str, token: str, limit: int = 15
) -> list[FlightPrice]:
    """Devuelve los `limit` vuelos mas baratos desde origin a cualquier destino,
    sin restriccion de fecha (la API busca en todo lo que tiene cacheado)."""
    response = requests.get(
        CHEAP_DESTINATIONS_URL,
        params={"origin": origin, "currency": currency, "token": token},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()

    if not payload.get("success"):
        return []

    flights = [
        _to_flight_price(origin, destination, currency, transfers_str, entry)
        for destination, entries_by_transfers in payload.get("data", {}).items()
        for transfers_str, entry in entries_by_transfers.items()
    ]
    flights = [flight for flight in flights if has_minimum_trip_length(flight)]
    flights.sort(key=lambda flight: flight.price)
    return flights[:limit]


def has_minimum_trip_length(flight: FlightPrice, min_nights: int = MIN_TRIP_NIGHTS) -> bool:
    """Descarta vuelos de ida y vuelta con menos de min_nights noches entre medias
    (un vuelo de ida y vuelta el mismo dia es barato pero no es un viaje real)."""
    if not flight.return_at:
        return True
    nights = (datetime.fromisoformat(flight.return_at) - datetime.fromisoformat(flight.departure_at)).days
    return nights >= min_nights


def _to_flight_price(origin: str, destination: str, currency: str, transfers_str: str, entry: dict) -> FlightPrice:
    return FlightPrice(
        origin=origin,
        destination=destination,
        price=entry["price"],
        currency=currency,
        departure_at=entry["departure_at"],
        return_at=entry.get("return_at"),
        airline=entry["airline"],
        transfers=int(transfers_str),
        booking_link=_search_link(origin, destination, entry["departure_at"], entry.get("return_at")),
    )


def _search_link(origin: str, destination: str, departure_at: str, return_at: str | None) -> str:
    departure_part = datetime.fromisoformat(departure_at).strftime("%d%m")
    if return_at:
        return_part = datetime.fromisoformat(return_at).strftime("%d%m")
        return f"https://www.aviasales.com/search/{origin}{departure_part}{destination}{return_part}1"
    return f"https://www.aviasales.com/search/{origin}{departure_part}{destination}1"
