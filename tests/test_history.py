from flight_hunter import history


def test_load_history_returns_empty_list_when_file_missing(tmp_path):
    assert history.load_history(tmp_path / "nope.json") == []


def test_record_deal_creates_the_file(tmp_path):
    path = tmp_path / "data" / "deal_history.json"
    history.record_deal(path, {"origin": "AGP", "destination": "IBZ", "price": 45})

    entries = history.load_history(path)
    assert len(entries) == 1
    assert entries[0]["origin"] == "AGP"
    assert "notified_at" in entries[0]


def test_record_deal_puts_newest_first(tmp_path):
    path = tmp_path / "deal_history.json"
    history.record_deal(path, {"destination": "OLD"})
    history.record_deal(path, {"destination": "NEW"})

    entries = history.load_history(path)
    assert entries[0]["destination"] == "NEW"
    assert entries[1]["destination"] == "OLD"


def test_record_deal_caps_at_max_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "MAX_ENTRIES", 3)
    path = tmp_path / "deal_history.json"
    for i in range(5):
        history.record_deal(path, {"destination": str(i)})

    entries = history.load_history(path)
    assert len(entries) == 3
    assert entries[0]["destination"] == "4"
