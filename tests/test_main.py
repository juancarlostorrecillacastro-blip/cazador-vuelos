from flight_hunter.api_client import FlightPrice
from flight_hunter.hotel_client import HotelOffer
from flight_hunter.main import build_history_entry


def _flight() -> FlightPrice:
    return FlightPrice(
        origin="AGP",
        destination="IBZ",
        price=45,
        currency="EUR",
        departure_at="2026-11-10T09:00:00+01:00",
        return_at="2026-11-15T20:00:00+01:00",
        airline="VY",
        transfers=0,
        booking_link="https://example.com/vuelo",
    )


def test_history_entry_without_hotel():
    entry = build_history_entry(_flight(), "buen precio", None)

    assert entry["origin"] == "AGP"
    assert entry["destination_name"] == "Ibiza"
    assert entry["price"] == 45
    assert "hotel_name" not in entry
    assert "total_price" not in entry


def test_history_entry_with_hotel_includes_total():
    hotel = HotelOffer(name="Apartamento Playa", total_price=170, currency="EUR", nights=5, link="https://example.com/hotel")
    entry = build_history_entry(_flight(), "buen precio", hotel)

    assert entry["hotel_name"] == "Apartamento Playa"
    assert entry["total_price"] == 215
