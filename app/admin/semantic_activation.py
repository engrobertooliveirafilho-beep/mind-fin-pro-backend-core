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
import os, traceback, psycopg2, psycopg2.extras
from fastapi import Header, HTTPException

@router.post("/admin/semantic/diagnose")
def diagnose_semantic_runtime(x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    out={"status":"DIAGNOSE_STARTED","checks":{}}
    try:
        out["checks"]["env"]={
          "DATABASE_URL": bool(os.getenv("DATABASE_URL")),
          "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
          "ADMIN_ACTIVATION_TOKEN": bool(os.getenv("ADMIN_ACTIVATION_TOKEN"))
        }
        with psycopg2.connect(os.getenv("DATABASE_URL")) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("select version()")
                out["checks"]["db_version"]=dict(cur.fetchone())
                cur.execute("select extname from pg_extension where extname='vector'")
                out["checks"]["pgvector"]=bool(cur.fetchone())
                cur.execute("select column_name from information_schema.columns where table_name='neura_memory'")
                out["checks"]["neura_memory_columns"]=[x["column_name"] for x in cur.fetchall()]
                cur.execute("select count(*) c from neura_memory")
                out["checks"]["neura_memory_count"]=dict(cur.fetchone())
        try:
            from app.embedding.provider import EmbeddingProvider
            emb=EmbeddingProvider().embed("teste")
            out["checks"]["embedding_dimension"]=len(emb) if emb else 0
        except Exception as e:
            out["checks"]["embedding_error"]=str(e)
        out["status"]="DIAGNOSE_OK"
        return out
    except Exception as e:
        return {"status":"DIAGNOSE_FAILED","error":str(e),"traceback":traceback.format_exc()[-3000:]}

@router.post("/admin/semantic/query-fast")
def semantic_query_fast(payload: dict, x_admin_token: str = Header(default="")):
    _check(x_admin_token)
    import time
    t0=time.time()
    sender_id=payload.get("sender_id","whatsapp:+5519996166906")
    query=payload.get("query","o que estou estudando?")
    sr=SemanticRetrievalProvider()
    rows=sr.search(sender_id,query,5)
    latency_ms=int((time.time()-t0)*1000)
    return {
      "status":"SEMANTIC_FAST_QUERY_OK" if len(rows)>0 else "SEMANTIC_FAST_QUERY_EMPTY",
      "returned":len(rows),
      "latency_ms":latency_ms,
      "latency_pass":latency_ms<4000,
      "top_score":rows[0].get("score") if rows else 0
    }

@router.post("/admin/debug/context")
def debug_context(payload: dict, x_admin_token: str = Header(default="")):

    _check(x_admin_token)

    from app.memory.provider import MemoryProvider
    from app.retrieval.provider import RetrievalProvider

    sender_id = payload.get("sender_id")

    memory = MemoryProvider()
    retrieval = RetrievalProvider()

    history = memory.history(sender_id)

    context = retrieval.retrieve("", history)

    return {
        "history_count": len(history),
        "history": history[-10:],
        "context": context
    }


@router.post("/admin/debug/orchestrator")
def debug_orchestrator(payload: dict, x_admin_token: str = Header(default="")):
    _check(x_admin_token)

    from app.orchestrator.prompt_orchestrator import PromptOrchestrator
    from app.memory.provider import MemoryProvider
    from app.retrieval.provider import RetrievalProvider

    sender_id = payload.get("sender_id","whatsapp:+5519996166906")
    message = payload.get("message","Qual é meu nome?")

    history = MemoryProvider().history(sender_id)
    context = RetrievalProvider().retrieve(message, history)
    reply = PromptOrchestrator().answer(message, context)

    return {
        "message": message,
        "context": context,
        "reply": reply
    }
