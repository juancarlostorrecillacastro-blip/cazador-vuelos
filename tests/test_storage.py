from flight_hunter import storage


def test_no_price_recorded_returns_none(tmp_path):
    db_path = tmp_path / "test.db"
    assert storage.get_best_notified_price(db_path, "MAD", "BCN") is None


def test_record_and_read_back_price(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", 32.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "BCN") == 32.0


def test_recording_again_updates_the_price(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", 32.0, "EUR")
    storage.record_notified_price(db_path, "MAD", "BCN", 25.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "BCN") == 25.0


def test_different_routes_dont_interfere(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", 32.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "LIS") is None
