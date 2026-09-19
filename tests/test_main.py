from fastapi.testclient import TestClient
from app.main import app, Calculator

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


def test_calculator_unit():
    calc = Calculator()
    assert calc.suma(10, 5) == 15
    assert calc.resta(10, 5) == 5
    assert calc.multiplicacion(4, 3) == 12
    assert calc.division(20, 4) == 5
    assert len(calc.historial) == 4


def test_calculator_endpoints():
    r_suma = client.post("/api/calculator/suma", json={"a": 15, "b": 5})
    assert r_suma.status_code == 200
    assert r_suma.json()["resultado"] == 20

    r_resta = client.post("/api/calculator/resta", json={"a": 15, "b": 5})
    assert r_resta.status_code == 200
    assert r_resta.json()["resultado"] == 10

    r_mult = client.post("/api/calculator/multiplicacion", json={"a": 6, "b": 7})
    assert r_mult.status_code == 200
    assert r_mult.json()["resultado"] == 42

    r_div = client.post("/api/calculator/division", json={"a": 50, "b": 2})
    assert r_div.status_code == 200
    assert r_div.json()["resultado"] == 25

    r_hist = client.get("/api/calculator/historial")
    assert r_hist.status_code == 200
    assert len(r_hist.json()["historial"]) >= 4
