from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

cases = [
    "quero deixar vc mais humanizada",
    "quais",
    "quero lançar a Eldora no WhatsApp",
]

def msg(xml):
    m = re.search(r"<Message>(.*?)</Message>", xml, re.S)
    return m.group(1).strip() if m else xml

for c in cases:
    r = client.post("/webhook/whatsapp", data={"From":"whatsapp:+5519996166906","Body":c})
    print("CASE:", c)
    print("STATUS:", r.status_code)
    print("LOCAL:", msg(r.text))
    print("---")
