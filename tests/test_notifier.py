from flight_hunter.api_client import FlightPrice
from flight_hunter.notifier import build_message


def _flight(transfers: int = 0, return_at: str | None = None) -> FlightPrice:
    return FlightPrice(
        origin="AGP",
        destination="STN",
        price=32,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        return_at=return_at,
        airline="FR",
        transfers=transfers,
        booking_link="https://example.com/reservar",
    )


def test_build_message_uses_codes_when_no_names_given():
    message = build_message(_flight())

    assert "AGP -> STN" in message


def test_build_message_uses_city_names_when_given():
    message = build_message(_flight(), origin_name="Malaga", destination_name="Londres")

    assert "Malaga (AGP) -> Londres (STN)" in message


def test_build_message_for_one_way_direct_flight():
    message = build_message(_flight())

    assert "32 EUR" in message
    assert "Ida: 24/11/2026 - directo - FR" in message
    assert "Vuelta" not in message
    assert "https://example.com/reservar" in message


def test_build_message_for_flight_with_stops():
    message = build_message(_flight(transfers=2))

    assert "2 escala(s)" in message


def test_build_message_for_round_trip():
    message = build_message(_flight(return_at="2026-11-28T07:45:00Z"))

    assert "Vuelta: 28/11/2026" in message


def test_build_message_includes_reason_when_given():
    message = build_message(_flight(), reason="precio muy por debajo de lo habitual")

    assert "Por que: precio muy por debajo de lo habitual" in message


def test_build_message_omits_reason_line_when_empty():
    message = build_message(_flight(), reason="")

    assert "Por que" not in message
