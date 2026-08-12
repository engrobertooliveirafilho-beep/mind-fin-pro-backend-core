from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("quero abrir uma franquia de sorvete", "+551199993001"),
    ("prossiga", "+551199993001"),
    ("como montar uma escola de inglês", "+551199993002"),
    ("quais", "+551199993002"),
    ("quero comprar uma máquina de algodão doce", "+551199993003"),
    ("continue", "+551199993003"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-" * 80)
