import os
import uuid
import psycopg2
import psycopg2.extras

from app.embedding.provider import EmbeddingProvider
from app.retrieval.semantic_provider import SemanticRetrievalProvider
from app.runtime.embedding_cache import cached_embed


def _database_url() -> str:
    db = os.getenv("DATABASE_URL")
    if not db:
        raise RuntimeError("DATABASE_URL not configured")
    return db


def _ensure_schema() -> None:
    with psycopg2.connect(_database_url(), connect_timeout=5) as conn:
        with conn.cursor() as cur:
            cur.execute("create extension if not exists vector")
            cur.execute("""
            create table if not exists neura_embeddings(
                id uuid primary key,
                sender_id text not null,
                message text not null,
                metadata jsonb default '{}'::jsonb,
                embedding vector(1536),
                created_at timestamptz default now()
            )
            """)
            cur.execute("create index if not exists neura_embeddings_sender_idx on neura_embeddings(sender_id)")
            cur.execute("create index if not exists neura_embeddings_vector_idx on neura_embeddings using ivfflat (embedding vector_cosine_ops) with (lists = 100)")
        conn.commit()


def insert_embedding(sender_id: str, text: str, metadata: dict | None = None) -> dict:
    if not text or not text.strip():
        return {"status": "skipped", "stored": False, "reason": "empty_text"}

    _ensure_schema()
    embedder = EmbeddingProvider()
    embedding = cached_embed(embedder, text)

    if not embedding:
        raise RuntimeError("embedding_provider_returned_empty")

    item_id = str(uuid.uuid4())
    payload = metadata or {}

    with psycopg2.connect(_database_url(), connect_timeout=5) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_embeddings(id, sender_id, message, metadata, embedding)
            values (%s, %s, %s, %s::jsonb, %s::vector)
            returning id, sender_id, message, metadata, created_at
            """, (item_id, sender_id or "default", text, psycopg2.extras.Json(payload), embedding))
            row = dict(cur.fetchone())
        conn.commit()

    return {"status": "ok", "stored": True, "id": str(row["id"]), "sender_id": row["sender_id"]}


def semantic_search(sender_id: str, query: str, limit: int = 5) -> list[dict]:
    return SemanticRetrievalProvider().search(sender_id or "default", query, limit)


def similarity_search(sender_id: str, query: str, top_k: int = 3) -> dict:
    rows = semantic_search(sender_id or "default", query, top_k)
    return {"status": "ok", "query": query, "results": rows}


def semantic_memory_recall(sender_id: str, query: str, top_k: int = 3) -> dict:
    return similarity_search(sender_id, query, top_k)


def store_memory(text: str, metadata: dict | None = None):
    sender_id = (metadata or {}).get("sender_id") or (metadata or {}).get("from") or "default"
    return insert_embedding(sender_id, text, metadata)


def retrieve_memory(query: str, top_k: int = 3):
    return similarity_search("default", query, top_k)


def semantic_graph_report():
    with psycopg2.connect(_database_url(), connect_timeout=5) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            select sender_id, count(*) as memories
            from neura_embeddings
            group by sender_id
            order by memories desc
            limit 50
            """)
            rows = [dict(x) for x in cur.fetchall()]
    return {"status": "ok", "source": "pgvector", "nodes_total": len(rows), "graph": rows}
