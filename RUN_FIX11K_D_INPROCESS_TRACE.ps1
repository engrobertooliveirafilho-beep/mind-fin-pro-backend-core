$ErrorActionPreference="Stop"
$ts=Get-Date -Format "yyyyMMdd_HHmmss"
$ev="_evidence\FIX11K_D_INPROCESS_TRACE_$ts"
New-Item -ItemType Directory -Force $ev | Out-Null

@"
import json, inspect, functools, time
from pathlib import Path
from fastapi.testclient import TestClient
import app.main as m

trace=[]

def log(hop, **kw):
    trace.append({"ts":time.time(),"hop":hop,"data":{k:str(v)[:4000] for k,v in kw.items()}})

def wrap(name):
    if not hasattr(m,name):
        log("missing_target", name=name)
        return
    fn=getattr(m,name)
    if not callable(fn):
        log("not_callable", name=name)
        return
    if inspect.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def aw(*a,**kw):
            log("before_"+name,args=a,kwargs=kw)
            out=await fn(*a,**kw)
            log("after_"+name,output=out)
            return out
        setattr(m,name,aw)
    else:
        @functools.wraps(fn)
        def sw(*a,**kw):
            log("before_"+name,args=a,kwargs=kw)
            out=fn(*a,**kw)
            log("after_"+name,output=out)
            return out
        setattr(m,name,sw)

for name in [
    "dispatch_single_runtime",
    "p4_12_whatsapp_live_ux_guard",
    "p4_12_context_lock",
    "p4_12b_factual_execution_lock",
    "factual_search_handoff",
    "strategic_conversation_authority",
    "final_conversational_arbiter",
    "_p412n_normalize_xml_response",
    "twiml",
    "safe_reply",
]:
    wrap(name)

client=TestClient(m.app)
msgs=["Oi","Tudo bem?","Quem é você?","Como você está?","Por que está dando erro?","Aprofunde","E depois?","Procure o erro principal","Quanto é 4x6"]
live=[]
for msg in msgs:
    log("inbound_message", message=msg)
    r=client.post("/webhook/whatsapp", data={"Body":msg,"From":"whatsapp:+559999999999"})
    log("final_xml", message=msg, status=r.status_code, body=r.text)
    live.append({"message":msg,"status":r.status_code,"response":r.text})

Path(r"$ev\REAL_HOP_TRACE.json").write_text(json.dumps(live,ensure_ascii=False,indent=2),encoding="utf-8")
Path(r"$ev\PIPELINE_TRACE_EVENTS.json").write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding="utf-8")

bad=["Vamos seguir pelo ponto real","Vamos aprofundar sem reiniciar"]
origins=[]
for i,e in enumerate(trace):
    txt=json.dumps(e,ensure_ascii=False)
    if any(b in txt for b in bad):
        origins.append({"index":i,"hop":e.get("hop"),"event":e})
Path(r"$ev\FALLBACK_ORIGIN_AUDIT.json").write_text(json.dumps(origins,ensure_ascii=False,indent=2),encoding="utf-8")

print("TRACE_EVENTS",len(trace))
print("ORIGINS",len(origins))
for o in origins[:20]:
    print(o["index"],o["hop"])
"@ | Set-Content "_fix11k_d_inprocess_trace.py" -Encoding UTF8

python _fix11k_d_inprocess_trace.py
rclone copy $ev "gdrive:MIND/CONTROL/FIX11K_D_INPROCESS_TRACE_$ts" --progress
Get-Content "$ev\FALLBACK_ORIGIN_AUDIT.json" -Raw
