from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
import os, json, uuid, urllib.request, urllib.parse

SCHEMA_SQL = """
create table if not exists eldora_messages(id bigserial primary key,user_id text,role text,content text,created_at timestamptz default now());
create table if not exists eldora_memory_facts(id bigserial primary key,user_id text,fact_key text,fact_value text,confidence float default 0.8,created_at timestamptz default now());
create table if not exists eldora_memory_edges(id bigserial primary key,user_id text,source_fact text,target_fact text,relation text,created_at timestamptz default now());
"""

SUPABASE_URL=(os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY=os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

def _enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def _headers(prefer="return=minimal"):
    h={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json"}
    if prefer: h["Prefer"]=prefer
    return h

def _insert_memory(user_id, memory_type, content, confidence=0.85, role="memory_graph"):
    if not _enabled():
        return {"ok":False,"saved":False,"backend":"local_only","reason":"SUPABASE_ENV_MISSING"}
    row={"id":str(uuid.uuid4()),"sender_id":str(user_id or "default")[:180],"memory_type":str(memory_type or "graph")[:80],"content":str(content or "")[:4000],"confidence":confidence,"message":str(content or "")[:4000],"role":role}
    try:
        req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/neura_memory",data=json.dumps(row).encode("utf-8"),headers=_headers(),method="POST")
        urllib.request.urlopen(req,timeout=8).read()
        return {"ok":True,"saved":True,"backend":"supabase_neura_memory","user_id":user_id}
    except Exception as e:
        return {"ok":False,"saved":False,"backend":"supabase_error","reason":str(e)[:240],"user_id":user_id}

def _fetch_memory(user_id, limit=12):
    if not _enabled():
        return []
    try:
        sender=urllib.parse.quote(str(user_id or "default")[:180],safe="")
        url=f"{SUPABASE_URL}/rest/v1/neura_memory?select=content,memory_type,confidence,created_at&sender_id=eq.{sender}&order=created_at.desc&limit={int(limit)}"
        req=urllib.request.Request(url,headers=_headers(prefer=None),method="GET")
        return json.loads(urllib.request.urlopen(req,timeout=8).read().decode("utf-8"))
    except Exception:
        return []

def save_message(user_id, role, content):
    return _insert_memory(user_id, f"message_{role}", content, 0.9, role="memory_graph_message")

def extract_memory_facts(message):
    facts=[]
    t=(message or "").lower()
    if "mind" in t: facts.append({"fact_key":"project","fact_value":"MIND","confidence":0.9})
    if "eldora" in t: facts.append({"fact_key":"agent","fact_value":"Eldora","confidence":0.9})
    if "roberto" in t: facts.append({"fact_key":"user_name","fact_value":"Roberto","confidence":0.95})
    if "matem" in t: facts.append({"fact_key":"topic","fact_value":"matemática","confidence":0.85})
    return facts

def upsert_memory_fact(user_id, fact):
    key=fact.get("fact_key","fact") if isinstance(fact,dict) else "fact"
    value=fact.get("fact_value",fact) if isinstance(fact,dict) else fact
    conf=fact.get("confidence",0.85) if isinstance(fact,dict) else 0.85
    return _insert_memory(user_id, f"fact_{key}", value, conf, role="memory_graph_fact")

def create_memory_edge(user_id, source_fact, target_fact, relation):
    content=json.dumps({"source_fact":source_fact,"target_fact":target_fact,"relation":relation},ensure_ascii=False)
    return _insert_memory(user_id, "memory_edge", content, 0.8, role="memory_graph_edge")

def retrieve_relevant_memory(user_id, query):
    rows=_fetch_memory(user_id)
    facts=extract_memory_facts(query)
    return {"facts":facts,"query":query,"persistent_rows":rows,"persistent_memory_count":len(rows),"backend":"supabase_neura_memory" if _enabled() else "local_only"}

def retrieve_user_profile(user_id):
    rows=_fetch_memory(user_id)
    content=" ".join([r.get("content","") for r in rows]).lower()
    return {"user_id":user_id,"known_name":"Roberto" if "roberto" in content else None,"dominant_project":"MIND" if "mind" in content else None,"persistent_memory_count":len(rows)}

def retrieve_project_context(user_id):
    rows=_fetch_memory(user_id)
    content=" ".join([r.get("content","") for r in rows]).lower()
    return {"project":"MIND" if "mind" in content else None,"agent":"Eldora" if "eldora" in content else None,"status":"persistent_memory_connected","persistent_memory_count":len(rows)}

def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)
