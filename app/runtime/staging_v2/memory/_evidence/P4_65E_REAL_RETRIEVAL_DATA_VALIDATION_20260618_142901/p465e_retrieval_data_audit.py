import os
import traceback

print("P4.65E_RETRIEVAL_DATA_AUDIT")

print("\n===== ENV CHECK =====")
for k in ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE", "SUPABASE_SERVICE_ROLE_KEY", "OPENAI_API_KEY"]:
    v = os.getenv(k)
    print(k, "=", "SET" if v else "MISSING")

print("\n===== PROVIDER INIT =====")
try:
    from app.retrieval.semantic_provider import SemanticRetrievalProvider
    p = SemanticRetrievalProvider()
    print("PROVIDER_OK")
    print("DATABASE_URL_IN_PROVIDER:", "SET" if p.db else "MISSING")
    print("EMBEDDER:", type(p.embedder).__name__)
except Exception:
    print("PROVIDER_ERROR")
    print(traceback.format_exc())
    p = None

print("\n===== EMBEDDING CHECK =====")
try:
    from app.embedding.provider import EmbeddingProvider
    from app.runtime.embedding_cache import cached_embed
    emb = cached_embed(EmbeddingProvider(), "P4.65E retrieval sentinel Eldora Drive knowledge graph")
    print("EMBEDDING_TYPE:", type(emb).__name__)
    print("EMBEDDING_LEN:", len(emb) if emb else 0)
    print("EMBEDDING_OK:", bool(emb))
except Exception:
    print("EMBEDDING_ERROR")
    print(traceback.format_exc())

print("\n===== DB TABLE CHECK =====")
try:
    import psycopg2
    import psycopg2.extras

    db = os.getenv("DATABASE_URL")
    if not db:
        print("DB_SKIPPED_DATABASE_URL_MISSING")
    else:
        with psycopg2.connect(db, connect_timeout=5) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    select count(*) as total
                    from neura_embeddings
                """)
                print("neura_embeddings_total:", dict(cur.fetchone()))

                cur.execute("""
                    select sender_id, count(*) as total
                    from neura_embeddings
                    group by sender_id
                    order by total desc
                    limit 20
                """)
                print("top_sender_ids:")
                for row in cur.fetchall():
                    print(dict(row))

                cur.execute("""
                    select sender_id, left(message, 220) as sample, metadata
                    from neura_embeddings
                    order by random()
                    limit 10
                """)
                print("random_samples:")
                for row in cur.fetchall():
                    print(dict(row))
except Exception:
    print("DB_TABLE_ERROR")
    print(traceback.format_exc())

print("\n===== DIRECT SEARCH DEFAULT SENDER =====")
if p:
    for sender in ["p465d_semantic_bridge", "default", "audit_user", "Roberto", "whatsapp", "mind", "eldora"]:
        try:
            rows = p.search(sender, "Eldora MIND Drive knowledge graph capability", limit=5)
            print("sender=", sender, "rows=", len(rows))
            for r in rows[:3]:
                print(" -", str(r.get("score")), str(r.get("message"))[:220])
        except Exception:
            print("SEARCH_ERROR sender=", sender)
            print(traceback.format_exc())

print("\nP4.65E_RETRIEVAL_DATA_AUDIT_COMPLETE")
