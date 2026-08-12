from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("quero validar estratégia FTMO", "+551199994001"),
    ("continue", "+551199994001"),
    ("quero abrir uma franquia de sorvete", "+551199994002"),
    ("prossiga", "+551199994002"),
    ("como montar uma escola de inglês", "+551199994003"),
    ("quais", "+551199994003"),
    ("quero emagrecer", "+551199994004"),
    ("quais", "+551199994004"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:900])
    print("-"*80)
