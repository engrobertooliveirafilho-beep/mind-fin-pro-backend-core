from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("quero emagrecer", "+551199991001"),
    ("quais", "+551199991001"),
    ("prossiga", "+551199991001"),
    ("quero humanizar você", "+551199991002"),
    ("quais são", "+551199991002"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:700])
    print("-"*80)
