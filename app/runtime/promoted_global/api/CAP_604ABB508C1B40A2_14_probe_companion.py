from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

cases = [
    ("como montar uma escola de inglês", "+551199998001"),
    ("quais", "+551199998001"),
    ("quero abrir uma franquia de sorvete", "+551199998002"),
    ("prossiga", "+551199998002"),
    ("quero emagrecer mas estou cansado e com dor no joelho", "+551199998003"),
    ("quais", "+551199998003"),
    ("meu objetivo é passar na FTMO com a MIND", "+551199998004"),
    ("continue", "+551199998004"),
]

for body, sender in cases:
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:1200])
    print("-"*80)
