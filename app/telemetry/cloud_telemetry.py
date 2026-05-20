import os, json, time, uuid, urllib.request

SUPABASE_URL=os.getenv("SUPABASE_URL","").rstrip("/")
SUPABASE_KEY=os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

def enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def classify_theme(text):
    t=(text or "").lower()
    if any(x in t for x in ["cane corso","ração","filhote","criador","doença","cachorro"]): return "pets_cane_corso"
    if any(x in t for x in ["humanização","humanizacao","eldora","runtime","rota","erro"]): return "eldora_runtime"
    if any(x in t for x in ["diesel","gasolina","ram 2500","ram 3500","motor"]): return "automotivo"
    if any(x in t for x in ["oi","bom dia","boa tarde","tudo bem"]): return "smalltalk"
    return "geral"

def classify_persona(text):
    t=(text or "").lower()
    if any(x in t for x in ["erro","problema","verificar","corrigir"]): return "debug_partner"
    if any(x in t for x in ["qual","como","por que","porque"]): return "explainer"
    if any(x in t for x in ["oi","bom dia","tudo bem"]): return "social_casual"
    return "general_assistant"

def _headers():
    return {"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=minimal"}

def log_event(sender_id, user_message, assistant_answer, kind="real", score=None):
    if not enabled():
        return {"ok":False,"reason":"SUPABASE_ENV_MISSING"}
    row={"id":str(uuid.uuid4()),"sender_id":sender_id or "unknown","kind":kind,"theme":classify_theme(user_message),"persona":classify_persona(user_message),"user_message":str(user_message or "")[:2000],"assistant_answer":str(assistant_answer or "")[:4000],"humanization_score":score,"created_at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    try:
        req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/eldora_conversation_events",data=json.dumps(row).encode("utf-8"),headers=_headers(),method="POST")
        urllib.request.urlopen(req,timeout=8).read()
        return {"ok":True}
    except Exception as e:
        return {"ok":False,"reason":str(e)[:240]}

def fetch_report(limit=1000):
    if not enabled():
        return {"ok":False,"reason":"SUPABASE_ENV_MISSING"}
    try:
        req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/eldora_conversation_events?select=kind,theme,persona,humanization_score,created_at&order=created_at.desc&limit={int(limit)}",headers={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}"},method="GET")
        rows=json.loads(urllib.request.urlopen(req,timeout=10).read().decode("utf-8"))
    except Exception as e:
        return {"ok":False,"reason":str(e)[:240]}
    by_theme={}; by_persona={}; by_kind={}; scores=[]
    for r in rows:
        by_theme[r.get("theme","unknown")]=by_theme.get(r.get("theme","unknown"),0)+1
        by_persona[r.get("persona","unknown")]=by_persona.get(r.get("persona","unknown"),0)+1
        by_kind[r.get("kind","unknown")]=by_kind.get(r.get("kind","unknown"),0)+1
        if isinstance(r.get("humanization_score"),(int,float)): scores.append(r["humanization_score"])
    return {"ok":True,"events_sampled":len(rows),"real_conversations":by_kind.get("real",0),"simulated_conversations":by_kind.get("simulation",0),"themes":by_theme,"personas":by_persona,"avg_humanization_score":round(sum(scores)/len(scores),2) if scores else None}
