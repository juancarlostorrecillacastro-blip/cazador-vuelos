"""Envia avisos de ofertas de vuelos por Telegram."""

from datetime import datetime

import requests

from flight_hunter.api_client import FlightPrice

SEND_MESSAGE_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_deal_alert(bot_token: str, chat_id: str, flight: FlightPrice) -> None:
    """Manda un mensaje de Telegram avisando de la oferta encontrada."""
    url = SEND_MESSAGE_URL.format(token=bot_token)
    message = build_message(flight)

    response = requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
    response.raise_for_status()


def build_message(flight: FlightPrice) -> str:
    """Construye el texto del aviso a partir de un FlightPrice."""
    fecha_ida = datetime.fromisoformat(flight.departure_at).strftime("%d/%m/%Y")
    escalas_ida = "directo" if flight.transfers == 0 else f"{flight.transfers} escala(s)"

    lines = [
        f"Oferta {flight.origin} -> {flight.destination}",
        f"Precio: {flight.price} {flight.currency}",
        f"Ida: {fecha_ida} - {escalas_ida} - {flight.airline}",
    ]

    if flight.return_at:
        fecha_vuelta = datetime.fromisoformat(flight.return_at).strftime("%d/%m/%Y")
        escalas_vuelta = (
            "directo" if flight.return_transfers == 0 else f"{flight.return_transfers} escala(s)"
        )
        lines.append(f"Vuelta: {fecha_vuelta} - {escalas_vuelta}")

    lines.append(flight.booking_link)
    return "\n".join(lines)
