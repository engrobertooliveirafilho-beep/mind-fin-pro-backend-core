from app.main import app
from fastapi.testclient import TestClient
import re

client = TestClient(app)

r = client.get("/health")
print("HEALTH", r.status_code, r.text[:300])

v = client.get("/version")
print("VERSION", v.status_code, v.text[:300])

w = client.post("/webhook/whatsapp", data={
    "From": "whatsapp:+5519996166906",
    "Body": "quero lançar a Eldora no WhatsApp"
})
print("WEBHOOK", w.status_code, w.text[:500])

assert r.status_code == 200
assert v.status_code == 200
assert w.status_code == 200
assert "Pra lançar a Eldora no WhatsApp" in w.text

print("STARTUP_SMOKE_OK")
