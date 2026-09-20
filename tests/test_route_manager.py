import pytest

from flight_hunter import route_manager


def test_extract_iata_code_from_city_option():
    assert route_manager.extract_iata_code("Madrid (MAD)") == "MAD"


def test_extract_iata_code_is_case_insensitive_and_trims_spaces():
    assert route_manager.extract_iata_code("  london (lhr)  ") == "LHR"


def test_extract_iata_code_rejects_text_without_a_code():
    with pytest.raises(ValueError):
        route_manager.extract_iata_code("Madrid")


def test_validate_month_accepts_correct_format():
    assert route_manager.validate_month("2026-11") == "2026-11"


def test_validate_month_rejects_wrong_format():
    with pytest.raises(ValueError):
        route_manager.validate_month("11-2026")
    with pytest.raises(ValueError):
        route_manager.validate_month("noviembre")


def test_add_and_load_routes(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("routes: []\n", encoding="utf-8")

    route_manager.add_route(
        config_path,
        {"origin": "MAD", "destination": "BCN", "max_price": 40, "currency": "EUR", "departure_month": "2026-11"},
    )

    routes = route_manager.load_routes(config_path)
    assert len(routes) == 1
    assert routes[0]["origin"] == "MAD"


def test_remove_route(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("routes: []\n", encoding="utf-8")

    route_manager.add_route(config_path, {"origin": "MAD", "destination": "BCN"})
    route_manager.add_route(config_path, {"origin": "MAD", "destination": "LIS"})

    route_manager.remove_route(config_path, 0)

    routes = route_manager.load_routes(config_path)
    assert len(routes) == 1
    assert routes[0]["destination"] == "LIS"
