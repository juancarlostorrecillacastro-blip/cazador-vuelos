from flight_hunter.api_client import FlightPrice
from flight_hunter.notifier import build_message


def test_build_message_for_direct_flight():
    flight = FlightPrice(
        origin="MAD",
        destination="BCN",
        price=32,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        airline="W4",
        transfers=0,
        booking_link="https://example.com/reservar",
    )

    message = build_message(flight)

    assert "MAD -> BCN" in message
    assert "32 EUR" in message
    assert "24/11/2026" in message
    assert "directo" in message
    assert "https://example.com/reservar" in message


def test_build_message_for_flight_with_stops():
    flight = FlightPrice(
        origin="MAD",
        destination="BCN",
        price=32,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        airline="W4",
        transfers=2,
        booking_link="https://example.com/reservar",
    )

    message = build_message(flight)

    assert "2 escala(s)" in message
