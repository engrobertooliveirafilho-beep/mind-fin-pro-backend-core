from fastapi.testclient import TestClient
from app.main import app

def test_contextual_followup_routes():
    c=TestClient(app)
    sender="whatsapp:+5519996166906"

    c.post("/webhook/whatsapp",data={"From":sender,"Body":"eu moro em jaguariuna, quero ir para holambra qual melhor caminho?"})
    r=c.post("/webhook/whatsapp",data={"From":sender,"Body":"quais?"})

    assert "incompleta" not in r.text.lower()

def test_contextual_followup_restaurants():
    c=TestClient(app)
    sender="whatsapp:+5519996166906"

    c.post("/webhook/whatsapp",data={"From":sender,"Body":"quais restaurantes devo conhecer em holambra?"})
    r=c.post("/webhook/whatsapp",data={"From":sender,"Body":"quais são?"})

    assert "incompleta" not in r.text.lower()
