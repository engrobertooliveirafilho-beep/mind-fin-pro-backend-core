from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def msg(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

cases = [
    "quero lançar a Eldora no WhatsApp",
    "como deixo você mais humanizada?",
    "como deixo a Eldora mais humana?",
]

bad = [
    "moto elétrica",
    "moto eletrica",
    "produto genérico",
    "produto/serviço",
]

for c in cases:
    r = client.post(
        "/webhook/whatsapp",
        data={"From":"whatsapp:+5519000001234","Body":c}
    )

    text = msg(r.text)

    print("CASE:", c)
    print("REPLY:", text)
    print("---")

    low = text.lower()

    for b in bad:
        assert b not in low

print("IDENTITY_LOCK_OK")
