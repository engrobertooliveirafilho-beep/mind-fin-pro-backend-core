from fastapi.testclient import TestClient
from app.main import app
from app.companionship.p19p31_p19p36_companion_runtime import get_profile

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_companion_school_depth():
    s = "+551111116001"
    a = send("como montar uma escola de inglês", s)
    b = send("quais", s)
    assert "escola" in b or "inglês" in b or "ingles" in b
    assert "alunos" in b or "professores" in b or "margem" in b or "público" in b or "publico" in b

def test_companion_franchise_depth():
    s = "+551111116002"
    a = send("quero abrir uma franquia de sorvete", s)
    b = send("prossiga", s)
    assert "franquia" in b or "sorvete" in b
    assert "royalties" in b or "payback" in b or "capital de giro" in b or "margem" in b

def test_companion_fitness_care_and_memory():
    s = "+551111116003"
    a = send("quero emagrecer mas estou cansado e com dor no joelho", s)
    b = send("quais", s)
    p = get_profile(s)
    assert "emagrecimento" in str(p).lower()
    assert "limitação" in str(p).lower() or "limitacao" in str(p).lower() or "física" in str(p).lower() or "fisica" in str(p).lower()
    assert "peso" in b or "treino" in b or "cardio" in b or "lesão" in b or "lesao" in b

def test_companion_trader_depth_and_trust():
    s = "+551111116004"
    a = send("meu objetivo é passar na FTMO com a MIND", s)
    b = send("continue", s)
    p = get_profile(s)
    assert "ftmo" in str(p).lower() or "mind trader" in str(p).lower()
    assert "trader" in b or "backtest" in b or "risco" in b or "timeframe" in b
