from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

def msg(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

cases = [
    "quero lançar a Eldora no WhatsApp",
    "como deixo vc mais humanizada? com mais emoção?",
    "quais são",
]

bad = [
    "resposta curta:",
    "resposta rápida:",
    "resposta:",
    "o que é eldora",
    "se for o robô",
    "se for um produto",
    "produto/serviço",
    "moto elétrica",
    "plataforma de chatbot",
    "tom de voz: use gírias",
]

for c in cases:
    r = client.post("/webhook/whatsapp", data={"From":"whatsapp:+5519000007777","Body":c})
    text = msg(r.text)
    print("CASE:", c)
    print("REPLY:", text)
    print("---")
    assert r.status_code == 200
    low = text.lower()
    for b in bad:
        assert b not in low, f"BAD={b} | {text}"

print("P19P26A_H8_XML_FILTER_OK")
