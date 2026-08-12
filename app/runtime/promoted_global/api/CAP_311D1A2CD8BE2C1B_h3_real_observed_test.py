from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def msg(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

cases = [
    ("whatsapp:+5519000000099", "conseguiu ver as novas implantações?"),
    ("whatsapp:+5519000000099", "como deixo vc mais humanizada? com mais emoção?"),
    ("whatsapp:+5519000000099", "quais são"),
    ("whatsapp:+5519000000002", "quero lançar a Eldora no WhatsApp"),
]

bad = [
    "resposta curta:",
    "para tornar uma interação com uma inteligência artificial",
    "você pode seguir algumas diretrizes",
    "pode considerar os seguintes pontos",
    "como posso ajudar",
    "poderia especificar",
]

for sender, body in cases:
    r = client.post("/webhook/whatsapp", data={"From": sender, "Body": body})
    text = msg(r.text)
    print("BODY:", body)
    print("REPLY:", text[:700])
    assert r.status_code == 200
    low = text.lower()
    for b in bad:
        assert b not in low, f"BAD_MARKER_FOUND={b} | {text}"
    print("---")

print("P19P26A_H3_REAL_HUMANIZATION_OK")
