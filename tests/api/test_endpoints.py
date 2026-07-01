from fastapi.testclient import TestClient

from hiremind.interfaces.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_copilot_endpoint_mock():
    response = client.post("/api/v1/copilot/query", json={"query": "test query"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "I couldn't find strong matches" in data["answer"]
