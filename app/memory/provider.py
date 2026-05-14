
import os, psycopg2
from psycopg2.extras import RealDictCursor

class MemoryProvider:
    def __init__(self):
        self.database_url=os.getenv("DATABASE_URL")
    def _conn(self):
        return psycopg2.connect(self.database_url)
    def save(self, sender_id, message):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("insert into neura_memory (sender_id, message, content) values (%s,%s,%s)", (sender_id, message, message))
        return True
    def history(self, sender_id, limit=20):
        with self._conn() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("select sender_id,message,content,created_at from neura_memory where sender_id=%s order by created_at desc limit %s", (sender_id, limit))
                return list(reversed(cur.fetchall()))
