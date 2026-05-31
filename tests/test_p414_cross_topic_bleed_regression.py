from fastapi.testclient import TestClient
from app.main import app

def test_vehicle_context_does_not_bleed_into_route():
    c=TestClient(app)
    s="whatsapp:+5519996166906"
    c.post("/webhook/whatsapp",data={"From":s,"Body":"quero comprar uma cb500 ano 2000 vale a pena?"})
    c.post("/webhook/whatsapp",data={"From":s,"Body":"e os pontos fracos?"})
    r=c.post("/webhook/whatsapp",data={"From":s,"Body":"moro em jaguariuna e quero ir pra São paulo, qual melhor caminho de carro?"})
    txt=r.text.lower()
    assert "moto" not in txt
    assert "manutenção" not in txt
    assert "documento" not in txt
    assert "são paulo" in txt or "sao paulo" in txt
