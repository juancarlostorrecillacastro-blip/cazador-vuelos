import pytest

from flight_hunter import web


@pytest.fixture
def client(tmp_path, monkeypatch):
    config_path = tmp_path / "config.yaml"
    config_path.write_text("routes: []\n", encoding="utf-8")
    monkeypatch.setattr(web, "CONFIG_PATH", config_path)
    web.app.config["TESTING"] = True
    with web.app.test_client() as test_client:
        yield test_client


def test_index_shows_empty_state(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Sin rutas vigiladas".encode() in response.data


def test_create_route_adds_it_and_redirects(client):
    response = client.post(
        "/routes",
        data={
            "origin": "Madrid (MAD)",
            "destination": "Barcelona (BCN)",
            "departure_month": "2026-11",
            "return_month": "",
            "max_price": "40",
            "currency": "EUR",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"MAD" in response.data
    assert "añadida".encode() in response.data


def test_create_route_with_invalid_city_shows_error(client):
    response = client.post(
        "/routes",
        data={
            "origin": "Madrid",
            "destination": "Barcelona (BCN)",
            "departure_month": "2026-11",
            "return_month": "",
            "max_price": "40",
            "currency": "EUR",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert "No se pudo añadir".encode() in response.data


def test_delete_route(client):
    client.post(
        "/routes",
        data={
            "origin": "Madrid (MAD)",
            "destination": "Barcelona (BCN)",
            "departure_month": "2026-11",
            "return_month": "",
            "max_price": "40",
            "currency": "EUR",
        },
    )

    response = client.post("/routes/0/delete", follow_redirects=True)

    assert "Sin rutas vigiladas".encode() in response.data
