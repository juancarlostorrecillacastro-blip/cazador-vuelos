from flight_hunter import airports


def test_known_code_returns_city_name():
    assert airports.city_name("AGP") == "Málaga"


def test_unknown_code_falls_back_to_the_code_itself():
    assert airports.city_name("ZZZ") == "ZZZ"
