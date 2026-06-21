from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_p19p29_fitness_context():
    s = "+551111111001"
    a = send("quero emagrecer", s)
    b = send("quais", s)
    c = send("prossiga", s)
    assert "peso" in b or "treino" in b or "cardio" in b
    assert "peso" in c or "treino" in c or "cardio" in c

def test_p19p29_agro_context():
    s = "+551111111002"
    a = send("como automatizar confinamento de boi", s)
    b = send("prossiga", s)
    assert "agro" in b or "animal" in b or "manejo" in b or "alimentação" in b

def test_p19p29_trader_context():
    s = "+551111111003"
    a = send("quero validar estratégia FTMO", s)
    b = send("continue", s)
    assert "trader" in b or "backtest" in b or "risco" in b or "timeframe" in b

def test_p19p29_unknown_short_followup_needs_topic():
    s = "+551111111004"
    a = send("prossiga", s)
    assert "assunto" in a or "tópico" in a or "topico" in a
