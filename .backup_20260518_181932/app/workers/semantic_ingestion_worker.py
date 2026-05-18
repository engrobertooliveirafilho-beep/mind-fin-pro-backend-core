import os, psycopg2, psycopg2.extras
from app.embedding.provider import EmbeddingProvider
def ingest_recent(limit=200):
    db=os.getenv("DATABASE_URL"); ep=EmbeddingProvider(); inserted=0
    with psycopg2.connect(db) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""create extension if not exists vector; create table if not exists neura_embeddings(id bigserial primary key,sender_id text not null,message text not null,source text default 'neura_memory',embedding vector(1536),metadata jsonb default '{}'::jsonb,created_at timestamptz default now()); create index if not exists neura_embeddings_vector_idx on neura_embeddings using ivfflat (embedding vector_cosine_ops);""")
            cur.execute("select sender_id, content as message from neura_memory where content is not null order by created_at desc limit %s",(limit,))
            rows=cur.fetchall()
            for r in rows:
                emb=ep.embed(r["message"])
                if emb:
                    cur.execute("insert into neura_embeddings(sender_id,message,embedding,metadata) values(%s,%s,%s::vector,%s)",(r["sender_id"],r["message"],emb,'{"worker":"semantic_ingestion"}'))
                    inserted+=1
        conn.commit()
    return {"inserted":inserted,"limit":limit}
if __name__=="__main__": print(ingest_recent())
