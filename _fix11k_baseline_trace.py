import functools, inspect, re
from fastapi.testclient import TestClient
import app.main as m

def wrap(name):
    fn=getattr(m,name,None)
    if not callable(fn):
        return

    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(*a,**kw):
            out=await fn(*a,**kw)
            print("="*120)
            print("FN:",name)
            print("ARGS:",str(a[:3])[:1000])
            print("OUT:",str(out)[:1500])
            return out
        setattr(m,name,aw)
    else:
        @functools.wraps(fn)
        def sw(*a,**kw):
            out=fn(*a,**kw)
            print("="*120)
            print("FN:",name)
            print("ARGS:",str(a[:3])[:1000])
            print("OUT:",str(out)[:1500])
            return out
        setattr(m,name,sw)

for x in [
"dispatch_single_runtime",
"strategic_conversation_authority",
"final_conversational_arbiter",
"_p412n_normalize_xml_response"
]:
    wrap(x)

c=TestClient(m.app)

for msg in [
"Oi",
"Quem é você?",
"Como você está?",
"Por que está dando erro?",
"Aprofunde",
"E depois?"
]:
    print("\n\nMSG=",msg)
    r=c.post("/webhook/whatsapp",data={"Body":msg,"From":"whatsapp:+559999999999"})
    clean=re.sub(r"<[^>]+>"," ",r.text).strip()
    print("FINAL=",clean)
