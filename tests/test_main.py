from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Diplomado" in data["message"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "diplomado-bd-api"


def test_get_database_stats():
    response = client.get("/api/stats")
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert "clientes" in data["data"]
        assert "ventas_olap" in data["data"]
