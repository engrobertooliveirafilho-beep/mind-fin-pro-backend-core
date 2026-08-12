import os, psycopg2, psycopg2.extras
from app.embedding.provider import EmbeddingProvider
from app.runtime.embedding_cache import cached_embed

class SemanticRetrievalProvider:

    def __init__(self):
        self.db=os.getenv("DATABASE_URL")
        self.embedder=EmbeddingProvider()
        self.last_error=None
        self.last_status={}

    def status(self):
        return {
            "database_url": bool(self.db),
            "embedding_model": getattr(self.embedder, "model", None),
            "embedding_last_error": getattr(self.embedder, "last_error", None),
            "last_error": self.last_error,
            "last_status": self.last_status,
        }

    def search(self,sender_id,query,limit=5):
        self.last_error=None
        self.last_status={"sender_id": sender_id, "query_len": len(str(query or ""))}

        try:
            emb=cached_embed(self.embedder, query)
        except Exception as e:
            self.last_error=f"embedding_exception:{type(e).__name__}:{str(e)[:300]}"
            return []

        if not emb:
            self.last_error=getattr(self.embedder, "last_error", None) or "embedding_empty"
            return []

        if not self.db:
            self.last_error="DATABASE_URL_MISSING"
            return []

        try:
            with psycopg2.connect(self.db, connect_timeout=3) as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                    cur.execute("""
                    select
                        message,
                        metadata,
                        sender_id,
                        1-(embedding <=> %s::vector) as score
                    from neura_embeddings
                    where sender_id=%s
                    order by embedding <=> %s::vector
                    limit %s
                    """,(emb,sender_id,emb,limit))

                    rows=[dict(x) for x in cur.fetchall()]

                    # P4.65E_BROAD_SEARCH_FALLBACK
                    if not rows:
                        cur.execute("""
                        select
                            message,
                            metadata,
                            sender_id,
                            1-(embedding <=> %s::vector) as score
                        from neura_embeddings
                        order by embedding <=> %s::vector
                        limit %s
                        """,(emb,emb,limit))
                        rows=[dict(x) for x in cur.fetchall()]

                    self.last_status["rows"] = len(rows)
                    return rows

        except Exception as e:
            self.last_error=f"db_exception:{type(e).__name__}:{str(e)[:500]}"
            return []
