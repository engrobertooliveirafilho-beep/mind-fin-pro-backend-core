from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_whatsapp_webhook_text():
    r = client.post("/webhook/whatsapp", data={"From":"whatsapp:+5511999999999","Body":"me explique derivadas"})
    assert r.status_code == 200
    assert "<Response>" in r.text
