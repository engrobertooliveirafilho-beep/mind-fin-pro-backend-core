import os, json, hashlib, math
from datetime import datetime, timezone

try:
    import psycopg2
except Exception:
    psycopg2 = None

MEMORY = []

def embed(text: str, dims: int = 16):
    h = hashlib.sha256(text.encode()).digest()
    return [round(((h[i] / 255.0) * 2 - 1), 6) for i in range(dims)]

def cosine(a, b):
    dot=sum(x*y for x,y in zip(a,b)); na=math.sqrt(sum(x*x for x in a)); nb=math.sqrt(sum(x*x for x in b))
    return 0.0 if na == 0 or nb == 0 else dot/(na*nb)

def _conn():
    url=os.getenv("DATABASE_URL")
    if not url or psycopg2 is None:
        return None
    return psycopg2.connect(url)

def store_persistent_memory(content: str, tenant_id: str="default", user_ref: str="anonymous", category: str="general", priority: int=1):
    vec = embed(content)
    item = {"content":content,"tenant_id":tenant_id,"user_ref":user_ref,"category":category,"embedding":vec,"priority":priority,"created_at":datetime.now(timezone.utc).isoformat()}
    conn=_conn()
    if not conn:
        MEMORY.append(item); return {"status":"ok","stored":True,"backend":"memory","item":item}
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "insert into eldora_cognitive_memory(tenant_id,user_ref,content,category,embedding,priority) values (%s,%s,%s,%s,%s,%s)",
                    (tenant_id,user_ref,content,category,"[" + ",".join(map(str, vec)) + "]",priority)
                )
        conn.close()
        return {"status":"ok","stored":True,"backend":"postgres_pgvector"}
    except Exception as e:
        try: conn.close()
        except Exception: pass
        item["postgres_error"]=str(e)
        MEMORY.append(item)
        return {"status":"ok","stored":True,"backend":"memory_fallback","item":item}

def retrieve_persistent_memory(query: str, top_k: int=5):
    q=embed(query)
    conn=_conn()
    results=[]
    if conn:
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("select content, category, priority, created_at from eldora_cognitive_memory order by embedding <=> %s::vector limit %s", ("[" + ",".join(map(str, q)) + "]", top_k))
                    for content, category, priority, created_at in cur.fetchall():
                        results.append({"content":content,"category":category,"priority":priority,"created_at":str(created_at),"backend":"postgres_pgvector"})
            conn.close()
            return {"status":"ok","query":query,"results":results}
        except Exception as e:
            try: conn.close()
            except Exception: pass
    scored=[]
    for item in MEMORY:
        score=cosine(q,item["embedding"]) + (item.get("priority",1)*0.01)
        scored.append({"score":score, **{k:v for k,v in item.items() if k!="embedding"}})
    scored.sort(key=lambda x:x["score"], reverse=True)
    return {"status":"ok","query":query,"results":scored[:top_k]}

def cognitive_store_report():
    return {"status":"ok","memory_fallback_items":len(MEMORY),"postgres_available":bool(os.getenv("DATABASE_URL") and psycopg2)}
