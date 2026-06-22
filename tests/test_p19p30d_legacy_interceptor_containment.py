from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_ftmo_continue_stays_trader():
    s = "+551111115001"
    a = send("quero validar estratégia FTMO", s)
    b = send("continue", s)
    assert "trader" in b or "backtest" in b or "risco" in b or "timeframe" in b
    assert "checklist ftmo" not in b

def test_school_quais_stays_subject():
    s = "+551111115002"
    a = send("como montar uma escola de inglês", s)
    b = send("quais", s)
    assert "escola" in b or "inglês" in b or "ingles" in b
    assert "holambra" not in b
    assert "restaurantes" not in b

def test_franchise_prossiga_stays_subject():
    s = "+551111115003"
    a = send("quero abrir uma franquia de sorvete", s)
    b = send("prossiga", s)
    assert "franquia" in b or "sorvete" in b
    assert "holambra" not in b

def test_fitness_quais_regression():
    s = "+551111115004"
    a = send("quero emagrecer", s)
    b = send("quais", s)
    assert "peso" in b or "treino" in b or "cardio" in b
