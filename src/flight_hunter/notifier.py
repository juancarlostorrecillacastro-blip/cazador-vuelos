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
    fecha = datetime.fromisoformat(flight.departure_at).strftime("%d/%m/%Y")
    escalas = "directo" if flight.transfers == 0 else f"{flight.transfers} escala(s)"

    return (
        f"Oferta {flight.origin} -> {flight.destination}\n"
        f"Precio: {flight.price} {flight.currency}\n"
        f"Salida: {fecha} - {escalas} - {flight.airline}\n"
        f"{flight.booking_link}"
    )
