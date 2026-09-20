"""Punto de entrada: busca chollos desde AGP y SVQ a cualquier destino y avisa por Telegram."""

import logging

from flight_hunter import ai_judge, api_client, config, deal_finder, notifier, storage

ORIGINS = ["AGP", "SVQ"]
CANDIDATES_PER_ORIGIN = 15

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    creds = config.load_credentials()
    for origin in ORIGINS:
        check_origin(origin, creds)


def check_origin(origin: str, creds: config.Credentials) -> None:
    flights = api_client.find_cheap_destinations(
        origin, "EUR", creds.travelpayouts_token, limit=CANDIDATES_PER_ORIGIN
    )
    logger.info("%s: %s candidatos mas baratos encontrados", origin, len(flights))

    verdicts = ai_judge.judge_deals(flights, creds.gemini_api_key)

    for flight, (is_deal, reason) in zip(flights, verdicts):
        check_flight(flight, is_deal, reason, creds)


def check_flight(flight: api_client.FlightPrice, is_deal: bool, reason: str, creds: config.Credentials) -> None:
    if not is_deal:
        logger.info(
            "%s -> %s: %s %s descartado (%s)",
            flight.origin, flight.destination, flight.price, flight.currency, reason,
        )
        return

    previous_best = storage.get_best_notified_price(storage.DEFAULT_DB_PATH, flight.origin, flight.destination)
    if not deal_finder.is_new_best_price(flight.price, previous_best):
        logger.info(
            "%s -> %s: %s %s ya se aviso antes, se omite",
            flight.origin, flight.destination, flight.price, flight.currency,
        )
        return

    notifier.send_deal_alert(creds.telegram_bot_token, creds.telegram_chat_id, flight, reason)
    storage.record_notified_price(
        storage.DEFAULT_DB_PATH, flight.origin, flight.destination, flight.price, flight.currency
    )
    logger.info(
        "Aviso enviado: %s -> %s a %s %s (%s)",
        flight.origin, flight.destination, flight.price, flight.currency, reason,
    )


if __name__ == "__main__":
    run()
