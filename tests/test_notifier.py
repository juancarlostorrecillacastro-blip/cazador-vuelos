from flight_hunter.api_client import FlightPrice
from flight_hunter.hotel_client import HotelOffer
from flight_hunter.notifier import build_message


def _flight(transfers: int = 0, return_at: str | None = None, price: float = 32) -> FlightPrice:
    return FlightPrice(
        origin="AGP",
        destination="STN",
        price=price,
        currency="EUR",
        departure_at="2026-11-24T09:55:00+01:00",
        return_at=return_at,
        airline="FR",
        transfers=transfers,
        booking_link="https://example.com/reservar?a=1&b=2",
    )


def _hotel(total_price: float = 170, nights: int = 5, name: str = "Hotel Ejemplo") -> HotelOffer:
    return HotelOffer(
        name=name,
        total_price=total_price,
        currency="EUR",
        nights=nights,
        link="https://www.hotels.com/ho123/",
    )


def test_build_message_uses_codes_when_no_names_given():
    message = build_message(_flight())
    assert "AGP → STN" in message


def test_build_message_uses_city_names_when_given():
    message = build_message(_flight(), origin_name="Malaga", destination_name="Londres")
    assert "Malaga (AGP) → Londres (STN)" in message


def test_build_message_shows_plain_price_without_hotel():
    message = build_message(_flight())
    assert "<b>Precio: 32 EUR</b>" in message
    assert "Total" not in message


def test_build_message_shows_breakdown_with_hotel():
    message = build_message(_flight(price=45), hotel=_hotel(total_price=170, nights=5))

    assert "Vuelo: 45 EUR" in message
    assert "Alojamiento (5 noches): 170 EUR" in message
    assert "<b>Total: 215 EUR</b>" in message


def test_build_message_for_flight_with_stops():
    message = build_message(_flight(transfers=2))
    assert "2 escala(s)" in message


def test_build_message_for_round_trip():
    message = build_message(_flight(return_at="2026-11-28T07:45:00Z"))
    assert "Vuelta: 28/11/2026" in message


def test_build_message_includes_reason_when_given():
    message = build_message(_flight(), reason="precio muy por debajo de lo habitual")
    assert "<i>precio muy por debajo de lo habitual</i>" in message


def test_build_message_escapes_html_special_characters_in_reason():
    message = build_message(_flight(), reason="barato & bueno")
    assert "barato &amp; bueno" in message


def test_build_message_omits_reason_line_when_empty():
    message = build_message(_flight(), reason="")
    assert "<i>" not in message


def test_build_message_links_have_readable_text_not_bare_urls():
    message = build_message(_flight(), hotel=_hotel())

    assert '<a href="https://example.com/reservar?a=1&amp;b=2">Ver vuelo</a>' in message
    assert '<a href="https://www.hotels.com/ho123/">Ver Hotel Ejemplo</a>' in message


def test_build_message_omits_hotel_link_when_no_hotel():
    message = build_message(_flight())
    assert "hotels.com" not in message
