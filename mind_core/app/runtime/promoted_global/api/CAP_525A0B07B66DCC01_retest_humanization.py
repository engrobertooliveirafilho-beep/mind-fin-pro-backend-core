from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

BAD_MARKERS = [
    "resposta curta:",
    "ação recomendada:",
    "diagnóstico:",
    "estratégia:",
    "execução:",
    "como posso ajudar",
    "poderia especificar",
]

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

for sender, body in cases:
    r = client.post("/webhook/whatsapp", data={"From": sender, "Body": body})
    text = msg(r.text)
    print("BODY:", body)
    print("REPLY:", text[:600])
    low = text.lower()
    assert r.status_code == 200
    for marker in BAD_MARKERS:
        assert marker not in low, f"BAD_MARKER_FOUND: {marker} | reply={text}"
    print("---")

print("P19P26A_HUMANIZATION_RETEST_OK")
