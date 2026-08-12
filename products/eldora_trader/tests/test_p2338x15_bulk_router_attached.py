from fastapi.testclient import TestClient

def test_mind_trader_bulk_router_attached():
    from app.main import app

    client = TestClient(app)
    r = client.get("/mind-trader/bulk-capabilities/health")

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "OK"
    assert data["mode"] == "PAPER_ONLY"
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["bulk_modules_total"] >= 1
