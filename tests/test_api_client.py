from flight_hunter.api_client import FlightPrice, has_minimum_trip_length


def _flight(departure_at: str, return_at: str | None) -> FlightPrice:
    return FlightPrice(
        origin="AGP",
        destination="FCO",
        price=50,
        currency="EUR",
        departure_at=departure_at,
        return_at=return_at,
        airline="FR",
        transfers=0,
        booking_link="https://example.com",
    )


def test_one_way_flight_always_passes():
    flight = _flight("2026-11-10T09:00:00+01:00", None)
    assert has_minimum_trip_length(flight) is True


def test_same_day_round_trip_is_rejected():
    flight = _flight("2026-11-10T09:00:00+01:00", "2026-11-10T20:00:00+01:00")
    assert has_minimum_trip_length(flight) is False


def test_round_trip_shorter_than_minimum_is_rejected():
    flight = _flight("2026-11-10T09:00:00+01:00", "2026-11-12T20:00:00+01:00")
    assert has_minimum_trip_length(flight) is False


def test_round_trip_at_exactly_the_minimum_passes():
    flight = _flight("2026-11-10T09:00:00+01:00", "2026-11-14T20:00:00+01:00")
    assert has_minimum_trip_length(flight) is True


def test_round_trip_longer_than_minimum_passes():
    flight = _flight("2026-11-10T09:00:00+01:00", "2026-11-20T20:00:00+01:00")
    assert has_minimum_trip_length(flight) is True


def test_custom_minimum_can_be_stricter():
    flight = _flight("2026-11-10T09:00:00+01:00", "2026-11-14T20:00:00+01:00")
    assert has_minimum_trip_length(flight, min_nights=7) is False
