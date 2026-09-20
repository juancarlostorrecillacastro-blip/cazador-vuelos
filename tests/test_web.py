import pytest

from flight_hunter import web


class _FakeAutomationControl:
    def __init__(self, initial_state: str):
        self.state = initial_state

    def get_workflow_state(self, repo, token):
        return self.state

    def set_workflow_enabled(self, repo, token, enabled):
        self.state = "active" if enabled else "disabled_manually"


class _FakeHistory:
    def __init__(self, entries=None):
        self.entries = entries or []

    def fetch_remote_history(self, repo):
        return self.entries


@pytest.fixture
def client(monkeypatch):
    fake = _FakeAutomationControl("disabled_manually")
    fake_history = _FakeHistory()
    monkeypatch.setattr(web, "automation_control", fake)
    monkeypatch.setattr(web, "history", fake_history)
    web.app.config["TESTING"] = True
    with web.app.test_client() as test_client:
        yield test_client, fake, fake_history


def test_index_shows_off_when_workflow_disabled(client):
    test_client, _, _ = client
    response = test_client.get("/")
    assert b"Apagado" in response.data


def test_index_shows_on_when_workflow_active(client):
    test_client, fake, _ = client
    fake.state = "active"
    response = test_client.get("/")
    assert "Buscando cada hora".encode() in response.data


def test_toggle_turns_it_on(client):
    test_client, fake, _ = client
    response = test_client.post("/toggle", follow_redirects=True)
    assert fake.state == "active"
    assert "activada".encode() in response.data


def test_toggle_turns_it_off(client):
    test_client, fake, _ = client
    fake.state = "active"
    response = test_client.post("/toggle", follow_redirects=True)
    assert fake.state == "disabled_manually"
    assert "desactivada".encode() in response.data


def test_historial_shows_empty_state(client):
    test_client, _, _ = client
    response = test_client.get("/historial")
    assert "Todavia no hay chollos".encode() in response.data


def test_historial_shows_entries(client):
    test_client, _, fake_history = client
    fake_history.entries = [
        {
            "origin": "AGP", "origin_name": "Malaga",
            "destination": "IBZ", "destination_name": "Ibiza",
            "price": 45, "currency": "EUR", "reason": "buen precio",
            "flight_link": "https://example.com/vuelo", "hotel_link": None,
            "notified_at": "2026-11-01T10:00:00+00:00",
        }
    ]
    response = test_client.get("/historial")

    assert b"Malaga (AGP)" in response.data
    assert b"Ibiza (IBZ)" in response.data
    assert "buen precio".encode() in response.data


def test_historial_shows_breakdown_when_hotel_present(client):
    test_client, _, fake_history = client
    fake_history.entries = [
        {
            "origin": "AGP", "origin_name": "Malaga",
            "destination": "IBZ", "destination_name": "Ibiza",
            "price": 45, "currency": "EUR", "reason": "",
            "flight_link": "https://example.com/vuelo",
            "hotel_link": "https://example.com/hotel", "hotel_name": "Apartamento Playa",
            "hotel_price": 170, "hotel_nights": 5, "total_price": 215,
            "notified_at": "2026-11-01T10:00:00+00:00",
        }
    ]
    response = test_client.get("/historial")

    assert "Total: 215 EUR".encode() in response.data
    assert "Apartamento Playa".encode() in response.data
