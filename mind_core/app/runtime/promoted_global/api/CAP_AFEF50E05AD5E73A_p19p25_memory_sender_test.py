from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def clean(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

sender_a = "whatsapp:+5519000000001"
sender_b = "whatsapp:+5519000000002"

cases = [
    (sender_a, "como automatizar confinamento de boi?"),
    (sender_a, "como eu faço?"),
    (sender_a, "e depois?"),
    (sender_b, "quero lançar a Eldora no WhatsApp"),
    (sender_b, "qual o próximo passo?"),
    (sender_a, "explique melhor"),
]

for sender, body in cases:
    r = client.post("/webhook/whatsapp", data={"From": sender, "Body": body})
    print("SENDER:", sender)
    print("BODY:", body)
    print("STATUS:", r.status_code)
    print("REPLY:", clean(r.text)[:500])
    print("---")

    assert r.status_code == 200
    assert "<Response>" in r.text
    assert "<Message>" in r.text
    low = r.text.lower()
    assert "como posso ajudar" not in low
    assert "poderia especificar" not in low

print("P19P25_MEMORY_SENDER_TEST_OK")
