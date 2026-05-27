import functools, inspect
import app.main as m
from fastapi.testclient import TestClient

def dump(name):
    fn=getattr(m,name,None)
    if not callable(fn):
        print("MISSING",name)
        return

    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(*a,**kw):
            out=await fn(*a,**kw)
            print("="*120)
            print("FN:",name)
            print("ARGS:",a[:3])
            print("OUT:",str(out)[:1500])
            return out
        setattr(m,name,aw)
    else:
        @functools.wraps(fn)
        def sw(*a,**kw):
            out=fn(*a,**kw)
            print("="*120)
            print("FN:",name)
            print("ARGS:",a[:3])
            print("OUT:",str(out)[:1500])
            return out
        setattr(m,name,sw)

for x in [
"dispatch_single_runtime",
"strategic_conversation_authority",
"final_conversational_arbiter"
]:
    dump(x)

c=TestClient(m.app)

for msg in [
"Quem é você?",
"Como você está?",
"Por que está dando erro?",
"Aprofunde",
"Quanto é 4x6"
]:
    print("\nMSG=",msg)
    r=c.post("/webhook/whatsapp",data={"Body":msg,"From":"whatsapp:+559999999999"})
    print("FINAL=",r.text[:1200])
