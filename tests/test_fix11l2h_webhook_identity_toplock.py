from fastapi.testclient import TestClient
from app.main import app

def test_webhook_identity_toplock_returns_eldora():
    client = TestClient(app)
    r = client.post("/webhook/whatsapp", data={"From":"whatsapp:+5519996166906","Body":"Quem é vc?"})
    assert r.status_code == 200
    assert "Sou a Eldora" in r.text
    assert "Não recebi conteúdo suficiente" not in r.text
