"""Envia avisos de chollos de vuelos por Telegram, con formato HTML."""

from datetime import datetime
from html import escape

import requests

from flight_hunter import airports
from flight_hunter.api_client import FlightPrice
from flight_hunter.hotel_client import HotelOffer

SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_deal_alert(
    bot_token: str,
    chat_id: str,
    flight: FlightPrice,
    reason: str = "",
    hotel: HotelOffer | None = None,
) -> None:
    """Manda un mensaje de Telegram avisando del chollo encontrado."""
    url = SEND_MESSAGE_URL.format(token=bot_token)
    origin_name = airports.city_name(flight.origin)
    destination_name = airports.city_name(flight.destination)
    message = build_message(flight, reason, origin_name, destination_name, hotel)

    response = requests.post(
        url,
        data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
        timeout=10,
    )
    response.raise_for_status()


def build_message(
    flight: FlightPrice,
    reason: str = "",
    origin_name: str = "",
    destination_name: str = "",
    hotel: HotelOffer | None = None,
) -> str:
    """Construye el texto del aviso con formato HTML (negritas, links con texto).
    Si se da un HotelOffer, muestra el desglose Vuelo + Alojamiento = Total."""
    fecha_ida = datetime.fromisoformat(flight.departure_at).strftime("%d/%m/%Y")
    escalas = "directo" if flight.transfers == 0 else f"{flight.transfers} escala(s)"

    origin_label = f"{origin_name} ({flight.origin})" if origin_name else flight.origin
    destination_label = (
        f"{destination_name} ({flight.destination})" if destination_name else flight.destination
    )

    lines = [f"<b>{escape(origin_label)} → {escape(destination_label)}</b>", ""]

    if hotel:
        total = flight.price + hotel.total_price
        lines.append(f"Vuelo: {flight.price:.0f} {flight.currency}")
        lines.append(f"Alojamiento ({hotel.nights} noches): {hotel.total_price:.0f} {hotel.currency}")
        lines.append(f"<b>Total: {total:.0f} {flight.currency}</b>")
    else:
        lines.append(f"<b>Precio: {flight.price:.0f} {flight.currency}</b>")

    lines.append("")
    lines.append(f"Ida: {fecha_ida} - {escalas} - {escape(flight.airline)}")

    if flight.return_at:
        fecha_vuelta = datetime.fromisoformat(flight.return_at).strftime("%d/%m/%Y")
        lines.append(f"Vuelta: {fecha_vuelta}")

    if reason:
        lines.append("")
        lines.append(f"<i>{escape(reason)}</i>")

    lines.append("")
    lines.append(f'<a href="{escape(flight.booking_link)}">Ver vuelo</a>')
    if hotel and hotel.link:
        lines.append(f'<a href="{escape(hotel.link)}">Ver {escape(hotel.name)}</a>')

    return "\n".join(lines)
