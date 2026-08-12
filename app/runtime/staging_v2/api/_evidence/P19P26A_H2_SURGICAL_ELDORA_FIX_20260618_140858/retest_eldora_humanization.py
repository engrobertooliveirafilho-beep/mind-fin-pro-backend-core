from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def msg(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

cases = [
    ("whatsapp:+5519000000002", "quero lançar a Eldora no WhatsApp"),
    ("whatsapp:+5519000000002", "qual o próximo passo?"),
    ("whatsapp:+5519000000002", "me explique melhor"),
    ("whatsapp:+5519000000001", "como automatizar confinamento de boi?"),
    ("whatsapp:+5519000000001", "como eu faço?"),
    ("whatsapp:+5519000000001", "e depois?"),
]

bad = ["resposta curta:", "ação recomendada:", "diagnóstico:", "estratégia:", "execução:", "como posso ajudar", "poderia especificar"]

for sender, body in cases:
    r = client.post("/webhook/whatsapp", data={"From": sender, "Body": body})
    text = msg(r.text)
    print("BODY:", body)
    print("REPLY:", text[:700])
    assert r.status_code == 200
    assert text.strip()
    low = text.lower()
    for b in bad:
        assert b not in low, f"BAD_MARKER_FOUND={b} | {text}"
    print("---")

print("P19P26A_H2_HUMANIZATION_OK")
