from flight_hunter.hotel_client import (
    extract_number,
    is_entire_place,
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


def test_is_entire_place_true_for_apartment_in_name():
    assert is_entire_place({"name": "Apartamentos Bon Sol Prestige"}) is True


def test_is_entire_place_true_when_amenities_include_kitchen():
    assert is_entire_place({"name": "Casa Rural Bonita", "short_amenities": ["Piscina", "Cocina"]}) is True


def test_is_entire_place_false_for_hostel():
    assert is_entire_place({"name": "Cisne by Nest Hostel"}) is False


def test_is_entire_place_false_for_plain_hotel_with_no_kitchen():
    assert is_entire_place({"name": "Hotel Central", "short_amenities": ["Piscina", "Wifi"]}) is False


def _property(display_price: str, name: str = "Apartamento Generico") -> dict:
    return {
        "name": name,
        "link": "/ho123/",
        "price": {"priceSummary": {"definition": {"displayPrice": display_price}}},
    }


def test_pick_cheapest_returns_the_lowest_priced_property():
    properties = [_property("300€", "Apartamento Caro"), _property("170€", "Apartamento Barato")]
    offer = pick_cheapest(properties, "EUR", nights=5)

    assert offer.name == "Apartamento Barato"
    assert offer.total_price == 170.0
    assert offer.nights == 5
    assert offer.link == "https://www.hotels.com/ho123/"


def test_pick_cheapest_skips_properties_without_a_readable_price():
    properties = [_property("Precio no disponible"), _property("120€", "Apartamento Unico")]
    offer = pick_cheapest(properties, "EUR", nights=3)

    assert offer.name == "Apartamento Unico"


def test_pick_cheapest_with_no_properties_returns_none():
    assert pick_cheapest([], "EUR", nights=5) is None


def test_pick_cheapest_skips_properties_with_null_price_summary():
    broken = {"name": "Apartamento Sin Precio", "link": "/ho1/", "price": {"priceSummary": None}}
    properties = [broken, _property("120€", "Apartamento Unico")]
    offer = pick_cheapest(properties, "EUR", nights=3)

    assert offer.name == "Apartamento Unico"


def test_pick_cheapest_ignores_shared_rooms_even_if_cheaper():
    hostel = _property("50€", "Cisne by Nest Hostel")
    apartment = _property("120€", "Apartamento Playa")
    offer = pick_cheapest([hostel, apartment], "EUR", nights=3)

    assert offer.name == "Apartamento Playa"


def test_pick_cheapest_returns_none_when_only_shared_rooms_available():
    hostel = _property("50€", "Cisne by Nest Hostel")
    assert pick_cheapest([hostel], "EUR", nights=3) is None
