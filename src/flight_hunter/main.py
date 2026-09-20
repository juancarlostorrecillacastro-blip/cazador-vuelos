"""Punto de entrada: recorre las rutas configuradas y avisa de ofertas nuevas."""

import logging

from flight_hunter import api_client, config, deal_finder, notifier, storage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def run() -> None:
    creds = config.load_credentials()
    search_config = config.load_search_config()
    routes = deal_finder.parse_routes(search_config)

    for route in routes:
        check_route(route, creds)


def check_route(route: deal_finder.RouteWatch, creds: config.Credentials) -> None:
    flight = api_client.find_cheapest_price(
        route.origin, route.destination, route.currency, creds.travelpayouts_token
    )

    if flight is None:
        logger.info("Sin resultados para %s -> %s", route.origin, route.destination)
        return

    if not deal_finder.is_a_deal(flight, route):
        logger.info(
            "%s -> %s: %s %s no es oferta (maximo %s)",
            route.origin, route.destination, flight.price, flight.currency, route.max_price,
        )
        return

    previous_best = storage.get_best_notified_price(
        storage.DEFAULT_DB_PATH, route.origin, route.destination
    )
    if not deal_finder.is_new_best_price(flight.price, previous_best):
        logger.info(
            "%s -> %s: %s %s ya se aviso antes, se omite",
            route.origin, route.destination, flight.price, flight.currency,
        )
        return

    notifier.send_deal_alert(creds.telegram_bot_token, creds.telegram_chat_id, flight)
    storage.record_notified_price(
        storage.DEFAULT_DB_PATH, route.origin, route.destination, flight.price, flight.currency
    )
    logger.info(
        "Aviso enviado: %s -> %s a %s %s", route.origin, route.destination, flight.price, flight.currency
    )


if __name__ == "__main__":
    run()
