from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(body, sender):
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("OUT:", r.text[:800])
    print("-"*80)

s = "+551199999901"
send("quero emagrecer", s)
send("quais", s)
send("prossiga", s)

s2 = "+551199999902"
send("quero humanizar você", s2)
send("quais são", s2)
