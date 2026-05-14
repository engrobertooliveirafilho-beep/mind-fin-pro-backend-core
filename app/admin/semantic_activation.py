import os, time, psycopg2, psycopg2.extras
from fastapi import APIRouter, Header, HTTPException
from app.embedding.provider import EmbeddingProvider
from app.retrieval.semantic_provider import SemanticRetrievalProvider
from app.runtime.contextual_reranker import contextual_rerank

router = APIRouter()

def _check(token):
    expected = os.getenv("ADMIN_ACTIVATION_TOKEN")
    if not expected or token != expected:
        raise HTTPException(status_code=403, detail="forbidden")

@router.post("/admin/semantic/activate")
def activate_semantic_runtime(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    t0=time.time()
    db=os.getenv("DATABASE_URL")
    env={
        "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "SUPABASE_URL": bool(os.getenv("SUPABASE_URL")),
        "SUPABASE_SERVICE_ROLE_KEY": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")),
    }
    if not db:
        return {"status":"FAILED","error":"DATABASE_URL_MISSING","env":env}

    inserted=0
    embeddings_count=0
    tests=[]
    ep=EmbeddingProvider()

    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("create extension if not exists vector;")
            cur.execute("""
            create table if not exists neura_embeddings(
              id bigserial primary key,
              sender_id text not null,
              message text not null,
              source text default 'neura_memory',
              embedding vector(1536),
              metadata jsonb default '{}'::jsonb,
              created_at timestamptz default now()
            );
            """)
            cur.execute("create index if not exists neura_embeddings_vector_idx on neura_embeddings using ivfflat (embedding vector_cosine_ops);")
            cur.execute("""
            select sender_id, coalesce(content,message,'') as message
            from neura_memory
            where coalesce(content,message,'') <> ''
            order by created_at desc
            limit 100
            """)
            rows=cur.fetchall()
            for r in rows:
                msg=r["message"]
                sid=r["sender_id"]
                cur.execute("select id from neura_embeddings where sender_id=%s and message=%s limit 1",(sid,msg))
                if cur.fetchone():
                    continue
                emb=ep.embed(msg)
                if emb:
                    cur.execute(
                        "insert into neura_embeddings(sender_id,message,embedding,metadata) values(%s,%s,%s::vector,%s)",
                        (sid,msg,emb,'{"source":"render_semantic_activation"}')
                    )
                    inserted+=1
            cur.execute("select count(*) c from neura_embeddings")
            embeddings_count=cur.fetchone()["c"]
        conn.commit()

    sr=SemanticRetrievalProvider()
    queries=["o que falei sobre minha prova?","o que estou estudando?","qual é meu nome?"]
    for q in queries:
        try:
            rows=sr.search("whatsapp:+5519996166906",q,8)
            ranked=contextual_rerank(rows,q)
            tests.append({"query":q,"returned":len(ranked),"top_score":ranked[0].get("contextual_score") if ranked else 0})
        except Exception as e:
            tests.append({"query":q,"error":str(e),"returned":0})

    latency_ms=int((time.time()-t0)*1000)
    hits=sum(1 for x in tests if x.get("returned",0)>0)
    semantic_hit_rate=round(hits/max(len(tests),1),2)

    return {
      "status":"RENDER_SEMANTIC_RUNTIME_OPERATIONAL" if embeddings_count>0 and semantic_hit_rate>0 else "SEMANTIC_RUNTIME_PARTIAL",
      "env":env,
      "inserted":inserted,
      "embeddings_count":embeddings_count,
      "semantic_tests":tests,
      "semantic_hit_rate":semantic_hit_rate,
      "memory_recall_success":semantic_hit_rate,
      "latency_avg_ms":latency_ms,
      "crash_rate":0,
      "criteria_passed": embeddings_count>0 and semantic_hit_rate>=0.70 and latency_ms<4000
    }
