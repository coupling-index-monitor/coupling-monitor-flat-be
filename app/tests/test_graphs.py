from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_dependency_graph():
    response = client.post("/api/graphs/")
    assert response.status_code == 200
    assert "graph" in response.json()
