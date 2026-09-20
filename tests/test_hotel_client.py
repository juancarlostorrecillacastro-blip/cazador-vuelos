from flight_hunter.hotel_client import (
    extract_number,
    nights_between,
    pick_cheapest,
    select_region_id,
)


def test_extract_number_from_euro_price():
    assert extract_number("170€") == 170.0


def test_extract_number_with_decimal_comma():
    assert extract_number("99,50€") == 99.5


def test_extract_number_returns_none_when_no_digits():
    assert extract_number("Precio no disponible") is None


def test_nights_between_computes_the_gap():
    assert nights_between("2026-11-10", "2026-11-15") == 5


def test_select_region_id_matches_by_airport_code():
    regions = [
        {"gaiaId": "1559", "hierarchyInfo": {"airport": {"airportCode": "XYZ"}}},
        {"gaiaId": "602653", "hierarchyInfo": {"airport": {"airportCode": "IBZ"}}},
    ]
    assert select_region_id(regions, "IBZ") == "602653"


def test_select_region_id_falls_back_to_first_result():
    regions = [
        {"gaiaId": "1559", "hierarchyInfo": {"airport": {"airportCode": "XYZ"}}},
        {"gaiaId": "602653", "hierarchyInfo": {}},
    ]
    assert select_region_id(regions, "IBZ") == "1559"


def test_select_region_id_with_no_results_returns_none():
    assert select_region_id([], "IBZ") is None


def _property(display_price: str, name: str = "Hotel") -> dict:
    return {
        "name": name,
        "link": "/ho123/",
        "price": {"priceSummary": {"definition": {"displayPrice": display_price}}},
    }


def test_pick_cheapest_returns_the_lowest_priced_property():
    properties = [_property("300€", "Caro"), _property("170€", "Barato")]
    offer = pick_cheapest(properties, "EUR", nights=5)

    assert offer.name == "Barato"
    assert offer.total_price == 170.0
    assert offer.nights == 5
    assert offer.link == "https://www.hotels.com/ho123/"


def test_pick_cheapest_skips_properties_without_a_readable_price():
    properties = [_property("Precio no disponible"), _property("120€", "Unico valido")]
    offer = pick_cheapest(properties, "EUR", nights=3)

    assert offer.name == "Unico valido"


def test_pick_cheapest_with_no_properties_returns_none():
    assert pick_cheapest([], "EUR", nights=5) is None


def test_pick_cheapest_skips_properties_with_null_price_summary():
    broken = {"name": "Sin precio", "link": "/ho1/", "price": {"priceSummary": None}}
    properties = [broken, _property("120€", "Unico valido")]
    offer = pick_cheapest(properties, "EUR", nights=3)

    assert offer.name == "Unico valido"
