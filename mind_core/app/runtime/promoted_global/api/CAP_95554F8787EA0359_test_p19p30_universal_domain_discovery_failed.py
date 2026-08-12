from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    assert r.status_code in (200, 201)
    return r.text.lower()

def test_p19p30_unknown_franchise_context():
    s = "+551111113001"
    a = send("quero abrir uma franquia de sorvete", s)
    b = send("prossiga", s)
    assert "franquia" in b or "sorvete" in b
    assert "mesmo assunto" in b or "continuando" in b

def test_p19p30_unknown_school_context():
    s = "+551111113002"
    a = send("como montar uma escola de inglês", s)
    b = send("quais", s)
    assert "escola" in b or "inglês" in b or "ingles" in b
    assert "continuando" in b or "mesmo assunto" in b

def test_p19p30_unknown_machine_context():
    s = "+551111113003"
    a = send("quero comprar uma máquina de algodão doce", s)
    b = send("continue", s)
    assert "máquina" in b or "maquina" in b or "algodão" in b or "algodao" in b

def test_p19p30_known_domains_still_work():
    s = "+551111113004"
    a = send("quero emagrecer", s)
    b = send("prossiga", s)
    assert "peso" in b or "treino" in b or "cardio" in b
