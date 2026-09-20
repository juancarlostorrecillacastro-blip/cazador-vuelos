"""Logica de decision: cuando un precio encontrado cuenta como 'oferta'."""

from dataclasses import dataclass

from flight_hunter.api_client import FlightPrice


@dataclass
class RouteWatch:
    origin: str
    destination: str
    max_price: float
    currency: str


def parse_routes(search_config: dict) -> list[RouteWatch]:
    """Convierte las rutas crudas del config.yaml en objetos RouteWatch."""
    return [
        RouteWatch(
            origin=route["origin"],
            destination=route["destination"],
            max_price=route["max_price"],
            currency=route["currency"],
        )
        for route in search_config["routes"]
    ]


def is_a_deal(flight: FlightPrice, route: RouteWatch) -> bool:
    """Un precio es oferta si es igual o menor al maximo configurado para esa ruta."""
    return flight.price <= route.max_price


def is_new_best_price(price: float, previous_best: float | None) -> bool:
    """Solo merece un aviso nuevo si no habia aviso previo, o si el precio bajo aun mas."""
    return previous_best is None or price < previous_best
