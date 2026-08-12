from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("quero emagrecer", "+551199991001"),
    ("quais", "+551199991001"),
    ("prossiga", "+551199991001"),
    ("como automatizar confinamento de boi", "+551199991002"),
    ("prossiga", "+551199991002"),
    ("quero validar estratégia FTMO", "+551199991003"),
    ("continue", "+551199991003"),
    ("prossiga", "+551199991004"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUTPUT:", r.text[:900])
    print("-" * 80)
