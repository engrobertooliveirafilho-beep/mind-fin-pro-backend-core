from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("quero validar estratégia FTMO", "+551199997001"),
    ("continue", "+551199997001"),
    ("como montar uma escola de inglês", "+551199997002"),
    ("quais", "+551199997002"),
    ("quero abrir uma franquia de sorvete", "+551199997003"),
    ("prossiga", "+551199997003"),
    ("quero emagrecer", "+551199997004"),
    ("quais", "+551199997004"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-"*80)
