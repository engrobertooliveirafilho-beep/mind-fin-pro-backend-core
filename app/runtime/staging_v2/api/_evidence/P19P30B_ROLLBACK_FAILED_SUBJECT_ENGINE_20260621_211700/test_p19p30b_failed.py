from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_unknown_franchise_subject_continues():
    s = "+551111114001"
    a = send("quero abrir uma franquia de sorvete", s)
    b = send("prossiga", s)
    assert "franquia" in b or "sorvete" in b
    assert "continuando" in b or "mesmo assunto" in b

def test_unknown_school_subject_continues():
    s = "+551111114002"
    a = send("como montar uma escola de inglês", s)
    b = send("quais", s)
    assert "escola" in b or "inglês" in b or "ingles" in b
    assert "continuando" in b or "mesmo assunto" in b

def test_unknown_machine_subject_continues():
    s = "+551111114003"
    a = send("quero comprar uma máquina de algodão doce", s)
    b = send("continue", s)
    assert "máquina" in b or "maquina" in b or "algodão" in b or "algodao" in b

def test_known_fitness_still_specialized():
    s = "+551111114004"
    a = send("quero emagrecer", s)
    b = send("quais", s)
    assert "peso" in b or "treino" in b or "cardio" in b
