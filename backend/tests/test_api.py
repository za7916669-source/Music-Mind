from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "MusicMind Similar Songs API is running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database_exists"] is True


def test_search():
    response = client.get(
        "/tracks/search",
        params={
            "q": "love",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "query" in data
    assert "total_results" in data
    assert "results" in data

    assert len(data["results"]) <= 5


def test_track_not_found():
    response = client.get(
        "/tracks/this_track_does_not_exist"
    )

    assert response.status_code == 404


def test_empty_search():
    response = client.get(
        "/tracks/search",
        params={"q": "   "},
    )

    assert response.status_code == 400