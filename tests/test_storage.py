from flight_hunter import storage


def test_no_price_recorded_returns_none(tmp_path):
    db_path = tmp_path / "test.db"
    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-11") is None


def test_record_and_read_back_price(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 32.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11") == 32.0


def test_recording_again_updates_the_price(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 32.0, "EUR")
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 25.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11") == 25.0


def test_different_routes_dont_interfere(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 32.0, "EUR")
    assert storage.get_best_notified_price(db_path, "MAD", "LIS", "2026-11", "2026-11") is None


def test_changing_the_month_resets_the_baseline(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 32.0, "EUR")
    # Mismo origen/destino, mes distinto: no deberia arrastrar el precio de noviembre
    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-12", "2026-12") is None


def test_one_way_and_round_trip_dont_interfere(tmp_path):
    db_path = tmp_path / "test.db"
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", None, 20.0, "EUR")
    storage.record_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11", 32.0, "EUR")

    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-11", None) == 20.0
    assert storage.get_best_notified_price(db_path, "MAD", "BCN", "2026-11", "2026-11") == 32.0
