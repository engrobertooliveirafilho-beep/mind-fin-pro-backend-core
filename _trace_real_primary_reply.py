from fastapi.testclient import TestClient
import app.main as m
import re

orig_dispatch=m.dispatch_single_runtime
orig_ctx=m.p4_12_context_lock
orig_factlock=m.p4_12b_factual_execution_lock
orig_handoff=m.factual_search_handoff
orig_auth=m.strategic_conversation_authority
orig_arb=m.final_conversational_arbiter

def log(name, before, after):
    print("="*120)
    print(name)
    print("IN :",repr(before)[:400])
    print("OUT:",repr(after)[:400])

def wrap(fn,name):
    def inner(*a,**kw):
        out=fn(*a,**kw)
        log(name,a,out)
        return out
    return inner

m.dispatch_single_runtime=wrap(orig_dispatch,"dispatch_single_runtime")
m.p4_12_context_lock=wrap(orig_ctx,"p4_12_context_lock")
m.p4_12b_factual_execution_lock=wrap(orig_factlock,"p4_12b_factual_execution_lock")
m.factual_search_handoff=wrap(orig_handoff,"factual_search_handoff")
m.strategic_conversation_authority=wrap(orig_auth,"strategic_conversation_authority")
m.final_conversational_arbiter=wrap(orig_arb,"final_conversational_arbiter")

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
