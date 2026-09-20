from flight_hunter.api_client import FlightPrice
from flight_hunter.notifier import build_message


def test_build_message_for_one_way_direct_flight():
    flight = FlightPrice(
        origin="MAD",
        destination="BCN",
        price=32,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        return_at=None,
        airline="W4",
        transfers=0,
        return_transfers=None,
        booking_link="https://example.com/reservar",
    )

    message = build_message(flight)

    assert "MAD -> BCN" in message
    assert "32 EUR" in message
    assert "Ida: 24/11/2026 - directo - W4" in message
    assert "Vuelta" not in message
    assert "https://example.com/reservar" in message


def test_build_message_for_flight_with_stops():
    flight = FlightPrice(
        origin="MAD",
        destination="BCN",
        price=32,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        return_at=None,
        airline="W4",
        transfers=2,
        return_transfers=None,
        booking_link="https://example.com/reservar",
    )

    message = build_message(flight)

    assert "2 escala(s)" in message


def test_build_message_for_round_trip():
    flight = FlightPrice(
        origin="MAD",
        destination="LON",
        price=44,
        currency="EUR",
        departure_at="2026-11-05T14:40:00+01:00",
        return_at="2026-11-08T07:45:00Z",
        airline="FR",
        transfers=0,
        return_transfers=1,
        booking_link="https://example.com/reservar",
    )

    message = build_message(flight)

    assert "Ida: 05/11/2026 - directo - FR" in message
    assert "Vuelta: 08/11/2026 - 1 escala(s)" in message
