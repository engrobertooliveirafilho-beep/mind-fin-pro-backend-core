from fastapi.testclient import TestClient
import re
import app.main as m

orig=m.whatsapp_webhook

async def traced(*args,**kwargs):
    r=await orig(*args,**kwargs)
    return r

m.whatsapp_webhook=traced

c=TestClient(m.app)

msgs=[
"Quem é você?",
"Como você está?",
"Por que está dando erro?",
"Aprofunde",
"E depois?"
]

for msg in msgs:
    print("="*120)
    print("MSG=",msg)

    r=c.post(
        "/webhook/whatsapp",
        data={
            "Body":msg,
            "From":"whatsapp:+559999999999"
        }
    )

    print("FINAL=",re.sub(r"<[^>]+>"," ",r.text).strip())
