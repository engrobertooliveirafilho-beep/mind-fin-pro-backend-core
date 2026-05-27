from fastapi.testclient import TestClient
import app.main as m
import re

orig_dispatch=m.dispatch_single_runtime
orig_fact=m.p4_12b_factual_execution_lock
orig_handoff=m.factual_search_handoff

def wrap(fn,name):
    def inner(*a,**kw):
        out=fn(*a,**kw)
        print("="*120)
        print(name)
        print("IN :",repr(a[:3])[:500])
        print("OUT:",repr(out)[:500])
        return out
    return inner

m.dispatch_single_runtime=wrap(orig_dispatch,"dispatch_single_runtime")
m.p4_12b_factual_execution_lock=wrap(orig_fact,"p4_12b_factual_execution_lock")
m.factual_search_handoff=wrap(orig_handoff,"factual_search_handoff")

c=TestClient(m.app)

for msg in [
"Quem é você?",
"Como você está?",
"Quanto é 4x6",
"E depois?"
]:
    print("\n\nMSG=",msg)
    r=c.post("/webhook/whatsapp",data={"Body":msg,"From":"whatsapp:+559999999999"})
    print("FINAL=",re.sub(r"<[^>]+>"," ",r.text).strip())
