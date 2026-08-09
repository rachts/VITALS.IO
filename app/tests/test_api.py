import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_analyze_no_auth():
    # The /api/analyze endpoint is now public to support demo mode
    # so this should return 200 OK
    payload = {
        "mrr": 500000,
        "total_customers": 500,
        "new_customers": 100,
        "churned_customers": 25,
        "ad_spend": 200000,
        "sales_cost": 150000,
        "cogs": 50000
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
