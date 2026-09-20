from flight_hunter.ai_judge import _parse_verdict


def test_parses_positive_verdict():
    is_deal, reason = _parse_verdict('{"es_chollo": true, "razon": "muy por debajo de lo habitual"}')
    assert is_deal is True
    assert reason == "muy por debajo de lo habitual"


def test_parses_negative_verdict():
    is_deal, reason = _parse_verdict('{"es_chollo": false, "razon": "precio normal para la ruta"}')
    assert is_deal is False
    assert reason == "precio normal para la ruta"


def test_invalid_json_defaults_to_not_a_deal():
    is_deal, reason = _parse_verdict("esto no es JSON")
    assert is_deal is False
    assert reason


def test_missing_reason_defaults_to_empty_string():
    is_deal, reason = _parse_verdict('{"es_chollo": true}')
    assert is_deal is True
    assert reason == ""
