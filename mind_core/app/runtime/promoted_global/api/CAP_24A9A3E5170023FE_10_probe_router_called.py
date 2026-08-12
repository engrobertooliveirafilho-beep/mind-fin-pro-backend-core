from fastapi.testclient import TestClient
from app.main import app

import app.domains.universal_domain_router as router

events = []
_original_route = router.route_domain_reply

def traced_route(text, ctx):
    events.append({
        "stage": "UNIVERSAL_ROUTER_CALLED",
        "text": text,
        "ctx": ctx
    })
    return _original_route(text, ctx)

router.route_domain_reply = traced_route

client = TestClient(app)

cases = [
    ("quero validar estratégia FTMO", "+551199996001"),
    ("continue", "+551199996001"),
    ("quero abrir uma franquia de sorvete", "+551199996002"),
    ("prossiga", "+551199996002"),
    ("como montar uma escola de inglês", "+551199996003"),
    ("quais", "+551199996003"),
    ("quero emagrecer", "+551199996004"),
    ("quais", "+551199996004"),
]

for body, sender in cases:
    before = len(events)
    r = client.post("/webhook/whatsapp", data={"Body": body, "From": sender})
    after = len(events)
    print("SENDER:", sender)
    print("INPUT:", body)
    print("STATUS:", r.status_code)
    print("ROUTER_CALLED:", after > before)
    print("OUT:", r.text[:900])
    print("-" * 80)

print("EVENTS:")
for e in events:
    print(e)
