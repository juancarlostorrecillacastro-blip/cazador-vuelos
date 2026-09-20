from flight_hunter.api_client import FlightPrice
from flight_hunter.deal_finder import RouteWatch, is_a_deal, parse_routes


def _flight(price: float) -> FlightPrice:
    return FlightPrice(
        origin="MAD",
        destination="BCN",
        price=price,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        airline="W4",
        transfers=1,
        booking_link="https://example.com",
    )


def test_price_below_max_is_a_deal():
    route = RouteWatch(origin="MAD", destination="BCN", max_price=40, currency="EUR")
    assert is_a_deal(_flight(32), route) is True


def test_price_equal_to_max_is_a_deal():
    route = RouteWatch(origin="MAD", destination="BCN", max_price=40, currency="EUR")
    assert is_a_deal(_flight(40), route) is True


def test_price_above_max_is_not_a_deal():
    route = RouteWatch(origin="MAD", destination="BCN", max_price=40, currency="EUR")
    assert is_a_deal(_flight(55), route) is False


def test_parse_routes_builds_route_watch_objects():
    config = {
        "routes": [
            {"origin": "MAD", "destination": "BCN", "max_price": 40, "currency": "EUR"},
            {"origin": "MAD", "destination": "LIS", "max_price": 60, "currency": "EUR"},
        ]
    }

    routes = parse_routes(config)

    assert routes == [
        RouteWatch(origin="MAD", destination="BCN", max_price=40, currency="EUR"),
        RouteWatch(origin="MAD", destination="LIS", max_price=60, currency="EUR"),
    ]
