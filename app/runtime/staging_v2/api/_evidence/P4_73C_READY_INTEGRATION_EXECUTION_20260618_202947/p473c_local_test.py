from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def clean(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

cases = [
    ("whatsapp:+551900004731", "quero deixar vc mais humanizada"),
    ("whatsapp:+551900004731", "quais"),
    ("whatsapp:+551900004732", "quero lançar a Eldora no WhatsApp"),
    ("whatsapp:+551900004732", "e depois?"),
]

bad = ["holambra", "sp-340", "casa bela", "moto elétrica", "produto/serviço", "como posso ajudar", "poderia especificar"]

for sender, body in cases:
    r = client.post("/webhook/whatsapp", data={"From": sender, "Body": body})
    text = clean(r.text)
    print("BODY:", body)
    print("REPLY:", text)
    print("---")
    assert r.status_code == 200
    low = text.lower()
    for b in bad:
        assert b not in low, f"BAD={b} | {text}"

print("P4_73C_READY_INTEGRATION_LOCAL_OK")
