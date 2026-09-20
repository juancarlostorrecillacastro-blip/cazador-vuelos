import pytest

from flight_hunter import web


class _FakeAutomationControl:
    def __init__(self, initial_state: str):
        self.state = initial_state

    def get_workflow_state(self, repo, token):
        return self.state

    def set_workflow_enabled(self, repo, token, enabled):
        self.state = "active" if enabled else "disabled_manually"


@pytest.fixture
def client(monkeypatch):
    fake = _FakeAutomationControl("disabled_manually")
    monkeypatch.setattr(web, "automation_control", fake)
    web.app.config["TESTING"] = True
    with web.app.test_client() as test_client:
        yield test_client, fake


def test_index_shows_off_when_workflow_disabled(client):
    test_client, _ = client
    response = test_client.get("/")
    assert b"Apagado" in response.data


def test_index_shows_on_when_workflow_active(client):
    test_client, fake = client
    fake.state = "active"
    response = test_client.get("/")
    assert "Buscando cada hora".encode() in response.data


def test_toggle_turns_it_on(client):
    test_client, fake = client
    response = test_client.post("/toggle", follow_redirects=True)
    assert fake.state == "active"
    assert "activada".encode() in response.data


def test_toggle_turns_it_off(client):
    test_client, fake = client
    fake.state = "active"
    response = test_client.post("/toggle", follow_redirects=True)
    assert fake.state == "disabled_manually"
    assert "desactivada".encode() in response.data
