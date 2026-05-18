import os, psycopg2, json
from fastapi import APIRouter, HTTPException, Header

router = APIRouter(prefix="/eldora/rag-live", tags=["eldora-rag-live"])

SCHEMA = """
create table if not exists eldora_rag_chunks (
  id bigserial primary key,
  source_id text not null,
  title text,
  content text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);
create index if not exists idx_eldora_rag_chunks_source on eldora_rag_chunks(source_id);
"""

def guard(token):
    expected=os.getenv("ADMIN_ACTIVATION_TOKEN")
    if expected and token != expected:
        raise HTTPException(403, "admin token invalid")

def db():
    url=os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(500, "DATABASE_URL missing")
    return psycopg2.connect(url)

@router.post("/schema/apply")
def schema_apply(x_admin_token: str | None = Header(default=None)):
    guard(x_admin_token)
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
        conn.commit()
    return {"schema_applied": True, "table": "eldora_rag_chunks"}

@router.post("/ingest")
def ingest(payload: dict, x_admin_token: str | None = Header(default=None)):
    guard(x_admin_token)
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
            cur.execute(
                "insert into eldora_rag_chunks(source_id,title,content,metadata) values(%s,%s,%s,%s) returning id",
                (payload.get("source_id","manual"), payload.get("title","untitled"), payload.get("content",""), json.dumps(payload.get("metadata",{})))
            )
            row=cur.fetchone()
        conn.commit()
    return {"ingest_ok": True, "chunk_id": row[0], "source_id": payload.get("source_id","manual")}

@router.post("/search")
def search(payload: dict, x_admin_token: str | None = Header(default=None)):
    guard(x_admin_token)
    q=(payload.get("query") or "").lower()
    with db() as conn:
        with conn.cursor() as cur:
            cur.execute("select id,source_id,title,content from eldora_rag_chunks where lower(content) like %s order by id desc limit 5", (f"%{q}%",))
            rows=cur.fetchall()
    return {"search_ok": True, "query": q, "results":[{"id":r[0],"source_id":r[1],"title":r[2],"content":r[3][:500]} for r in rows]}

@router.post("/answer")
def answer(payload: dict, x_admin_token: str | None = Header(default=None)):
    s=search(payload, x_admin_token)
    if not s["results"]:
        return {"answer_ok": True, "answer": "Não encontrei fonte suficiente no índice.", "citations": []}
    top=s["results"][0]
    return {"answer_ok": True, "answer": f"Com base na fonte {top['source_id']}: {top['content'][:240]}", "citations":[{"source_id":top["source_id"],"chunk_id":top["id"],"title":top["title"]}]}
