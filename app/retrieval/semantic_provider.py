import os, psycopg2, psycopg2.extras
from app.embedding.provider import EmbeddingProvider
from app.runtime.embedding_cache import cached_embed

class SemanticRetrievalProvider:

    def __init__(self):
        self.db=os.getenv("DATABASE_URL")
        self.embedder=EmbeddingProvider()

    def search(self,sender_id,query,limit=5):

        emb=cached_embed(self.embedder, query)

        if not emb:
            return []

        with psycopg2.connect(self.db, connect_timeout=3) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:

                cur.execute("""
                select
                    message,
                    metadata,
                    1-(embedding <=> %s::vector) as score
                from neura_embeddings
                where sender_id=%s
                order by embedding <=> %s::vector
                limit %s
                """,(emb,sender_id,emb,limit))

                rows=[dict(x) for x in cur.fetchall()]

                return rows
