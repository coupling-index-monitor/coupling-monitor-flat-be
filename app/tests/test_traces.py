from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_collect_traces():
    response = client.post("/api/traces/service-a")
    assert response.status_code == 200
    assert "traces_collected" in response.json()
