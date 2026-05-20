from datetime import datetime, timezone
import os, json, uuid, urllib.request

SOCIAL_MEMORY=[]

SUPABASE_URL=(os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY=os.getenv("SUPABASE_SERVICE_ROLE") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""

def _enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)

def _headers(prefer="return=minimal"):
    h={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json"}
    if prefer: h["Prefer"]=prefer
    return h

def store_social_memory(user_id:str, interaction:str, affinity:float=0.9):
    item={"memory_id":str(uuid.uuid4()),"user_id":user_id,"interaction":interaction,"affinity":affinity,"created_at":datetime.now(timezone.utc).isoformat()}
    SOCIAL_MEMORY.append(item)

    if _enabled():
        row={"id":item["memory_id"],"sender_id":str(user_id or "default")[:180],"memory_type":"social_memory","content":str(interaction or "")[:4000],"confidence":float(affinity),"message":str(interaction or "")[:4000],"role":"social_memory"}
        try:
            req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/neura_memory",data=json.dumps(row).encode("utf-8"),headers=_headers(),method="POST")
            urllib.request.urlopen(req,timeout=8).read()
            return {"status":"ok","backend":"supabase_neura_memory","memory":item,"total_memories":len(SOCIAL_MEMORY)}
        except Exception as e:
            return {"status":"ok","backend":"local_fallback","supabase_error":str(e)[:240],"memory":item,"total_memories":len(SOCIAL_MEMORY)}

    return {"status":"ok","backend":"local_fallback","memory":item,"total_memories":len(SOCIAL_MEMORY)}

def social_memory_report():
    if _enabled():
        try:
            req=urllib.request.Request(f"{SUPABASE_URL}/rest/v1/neura_memory?select=sender_id,content,confidence,created_at&memory_type=eq.social_memory&order=created_at.desc&limit=100",headers=_headers(prefer=None),method="GET")
            rows=json.loads(urllib.request.urlopen(req,timeout=8).read().decode("utf-8"))
            return {"status":"ok","backend":"supabase_neura_memory","total_memories":len(rows),"memories":rows}
        except Exception as e:
            return {"status":"partial","backend":"local_fallback","supabase_error":str(e)[:240],"total_memories":len(SOCIAL_MEMORY),"memories":SOCIAL_MEMORY[-100:]}

    return {"status":"ok","backend":"local_fallback","total_memories":len(SOCIAL_MEMORY),"memories":SOCIAL_MEMORY[-100:]}
