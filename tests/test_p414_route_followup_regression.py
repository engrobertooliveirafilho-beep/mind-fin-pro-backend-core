from fastapi.testclient import TestClient
from app.main import app

def test_route_followup_after_campinas():
    c=TestClient(app)
    s="whatsapp:+5519996166906"

    c.post("/webhook/whatsapp",data={"From":s,"Body":"moro em jaguariuna e quero ir pra sao paulo, qual melhor caminho de carro?"})
    r=c.post("/webhook/whatsapp",data={"From":s,"Body":"depois de campinas vou pra onde?"})

    txt=r.text.lower()
    assert "depende do seu destino" not in txt
    assert "rodovia" in txt or "anhanguera" in txt or "bandeirantes" in txt

def test_route_followup_e_depois():
    c=TestClient(app)
    s="whatsapp:+5519996166906"

    c.post("/webhook/whatsapp",data={"From":s,"Body":"moro em jaguariuna e quero ir pra sao paulo, qual melhor caminho de carro?"})
    r=c.post("/webhook/whatsapp",data={"From":s,"Body":"e depois?"})

    assert "o que acontece depois" not in r.text.lower()
