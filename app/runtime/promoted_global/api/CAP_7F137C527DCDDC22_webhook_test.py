from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

cases = [
    {"From":"whatsapp:+5519999999999","Body":"como automatizar confinamento de boi?"},
    {"From":"whatsapp:+5519999999999","Body":"como eu faço?"},
    {"From":"whatsapp:+5519999999999","Body":"e depois?"},
    {"From":"whatsapp:+5519999999999","Body":"explique melhor"},
    {"From":"whatsapp:+5519999999999","Body":"qual o próximo passo?"},
]

for c in cases:
    r = client.post("/webhook/whatsapp", data=c)
    print("CASE:", c["Body"])
    print("STATUS:", r.status_code)
    print("BODY:", r.text[:500].replace("\n"," "))
    assert r.status_code == 200
    assert "<Response>" in r.text
    assert "<Message>" in r.text
    assert "como posso ajudar" not in r.text.lower()
    assert "poderia especificar" not in r.text.lower()
    print("---")

print("WEBHOOK_TEST_OK")
