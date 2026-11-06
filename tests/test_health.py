from fastapi.testclient import TestClient

from app.main import create_app


def test_healthz_and_readyz() -> None:
    client = TestClient(create_app())

    health_response = client.get("/healthz")
    ready_response = client.get("/readyz")

    assert health_response.status_code == 200
    assert health_response.json()["status"] == "ok"

    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"
