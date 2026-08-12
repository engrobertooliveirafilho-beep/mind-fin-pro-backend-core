from fastapi.testclient import TestClient

def test_mind_trader_institutional_router_attached():
    from app.main import app

    client = TestClient(app)
    r = client.get("/mind-trader/institutional/health")

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "OK"
    assert data["mode"] == "PAPER_ONLY"
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
