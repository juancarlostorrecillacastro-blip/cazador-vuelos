"""Envia avisos de chollos de vuelos por Telegram."""

from datetime import datetime

import requests

from flight_hunter.api_client import FlightPrice

SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_deal_alert(bot_token: str, chat_id: str, flight: FlightPrice, reason: str = "") -> None:
    """Manda un mensaje de Telegram avisando del chollo encontrado."""
    url = SEND_MESSAGE_URL.format(token=bot_token)
    message = build_message(flight, reason)

    response = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    response.raise_for_status()


def build_message(flight: FlightPrice, reason: str = "") -> str:
    """Construye el texto del aviso a partir de un FlightPrice y el motivo de Claude."""
    fecha_ida = datetime.fromisoformat(flight.departure_at).strftime("%d/%m/%Y")
    escalas = "directo" if flight.transfers == 0 else f"{flight.transfers} escala(s)"

    lines = [
        f"Chollo {flight.origin} -> {flight.destination}",
        f"Precio: {flight.price} {flight.currency}",
        f"Ida: {fecha_ida} - {escalas} - {flight.airline}",
    ]

    if flight.return_at:
        fecha_vuelta = datetime.fromisoformat(flight.return_at).strftime("%d/%m/%Y")
        lines.append(f"Vuelta: {fecha_vuelta}")

    if reason:
        lines.append(f"Por que: {reason}")

    lines.append(flight.booking_link)
    return "\n".join(lines)
