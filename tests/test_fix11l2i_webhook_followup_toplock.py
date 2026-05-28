from fastapi.testclient import TestClient
from app.main import app

def test_webhook_followup_toplock_not_empty():
    client = TestClient(app)
    r = client.post("/webhook/whatsapp", data={"From":"whatsapp:+5519996166906","Body":"Aprofunde"})
    assert r.status_code == 200
    assert "Não recebi conteúdo suficiente" not in r.text
    assert "Execução contextual" in r.text
