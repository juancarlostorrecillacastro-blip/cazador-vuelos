from flight_hunter.ai_judge import _parse_batch_verdict


def test_parses_batch_verdict_in_order():
    text = (
        '[{"es_chollo": true, "razon": "muy barato"}, '
        '{"es_chollo": false, "razon": "precio normal"}]'
    )
    results = _parse_batch_verdict(text, expected=2)

    assert results == [(True, "muy barato"), (False, "precio normal")]


def test_strips_markdown_code_fence():
    text = '```json\n[{"es_chollo": true, "razon": "chollo"}]\n```'
    results = _parse_batch_verdict(text, expected=1)

    assert results == [(True, "chollo")]


def test_invalid_json_defaults_all_to_not_a_deal():
    results = _parse_batch_verdict("esto no es JSON", expected=3)

    assert results == [(False, "No se pudo interpretar la respuesta de la IA")] * 3


def test_wrong_length_defaults_all_to_not_a_deal():
    text = '[{"es_chollo": true, "razon": "chollo"}]'
    results = _parse_batch_verdict(text, expected=2)

    assert results == [(False, "No se pudo interpretar la respuesta de la IA")] * 2


def test_missing_reason_defaults_to_empty_string():
    results = _parse_batch_verdict('[{"es_chollo": true}]', expected=1)

    assert results == [(True, "")]
