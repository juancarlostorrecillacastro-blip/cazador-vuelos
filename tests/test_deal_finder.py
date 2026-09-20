from flight_hunter.api_client import FlightPrice
from flight_hunter.deal_finder import RouteWatch, is_a_deal, is_new_best_price, parse_routes


def _flight(price: float) -> FlightPrice:
    return FlightPrice(
        origin="MAD",
        destination="BCN",
        price=price,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        return_at=None,
        airline="W4",
        transfers=1,
        return_transfers=None,
        booking_link="https://example.com",
    )


def _route(max_price: float) -> RouteWatch:
    return RouteWatch(
        origin="MAD",
        destination="BCN",
        max_price=max_price,
        currency="EUR",
        departure_month="2026-11",
    )


def test_price_below_max_is_a_deal():
    assert is_a_deal(_flight(32), _route(40)) is True


def test_price_equal_to_max_is_a_deal():
    assert is_a_deal(_flight(40), _route(40)) is True


def test_price_above_max_is_not_a_deal():
    assert is_a_deal(_flight(55), _route(40)) is False


def test_is_new_best_price_when_no_previous_record():
    assert is_new_best_price(32, None) is True


def test_is_new_best_price_when_price_dropped():
    assert is_new_best_price(25, 32) is True


def test_is_new_best_price_when_price_did_not_improve():
    assert is_new_best_price(32, 32) is False
    assert is_new_best_price(40, 32) is False


def test_parse_routes_builds_route_watch_objects():
    config = {
        "routes": [
            {
                "origin": "MAD",
                "destination": "BCN",
                "max_price": 40,
                "currency": "EUR",
                "departure_month": "2026-11",
                "return_month": "2026-12",
            },
            {
                "origin": "MAD",
                "destination": "LIS",
                "max_price": 60,
                "currency": "EUR",
                "departure_month": "2026-11",
            },
        ]
    }

    routes = parse_routes(config)

    assert routes == [
        RouteWatch(
            origin="MAD",
            destination="BCN",
            max_price=40,
            currency="EUR",
            departure_month="2026-11",
            return_month="2026-12",
        ),
        RouteWatch(
            origin="MAD",
            destination="LIS",
            max_price=60,
            currency="EUR",
            departure_month="2026-11",
        ),
    ]
