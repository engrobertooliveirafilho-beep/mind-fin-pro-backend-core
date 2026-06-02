
import os
import uuid
import psycopg2
import psycopg2.extras

def _db():
    return os.getenv("DATABASE_URL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS neura_visual_memory (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  media_url TEXT NOT NULL,
  media_type TEXT,
  source TEXT DEFAULT 'whatsapp',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS neura_visual_analysis (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  media_id BIGINT,
  analysis TEXT NOT NULL,
  labels JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

def ensure_visual_schema():
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
        conn.commit()
    return {"ok": True}

def save_visual_media(sender_id: str, media_url: str, media_type: str = "", source: str = "whatsapp") -> dict:
    ensure_visual_schema()
    if not sender_id or not media_url:
        return {"ok": False, "error": "sender_id_or_media_url_missing"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_visual_memory(sender_id,media_url,media_type,source)
            values (%s,%s,%s,%s)
            returning *
            """,(sender_id,media_url,media_type,source))
            row=dict(cur.fetchone())
        conn.commit()
    return {"ok": True, "media": row}

def get_last_visual_media(sender_id: str) -> dict:
    ensure_visual_schema()
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            select * from neura_visual_memory
            where sender_id=%s
            order by created_at desc
            limit 1
            """,(sender_id,))
            row=cur.fetchone()
    return {"ok": True, "media": dict(row) if row else None}

def save_visual_analysis(sender_id: str, analysis: str, media_id: int | None = None, labels: list | None = None) -> dict:
    ensure_visual_schema()
    if not sender_id or not analysis:
        return {"ok": False, "error": "sender_id_or_analysis_missing"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_visual_analysis(sender_id,media_id,analysis,labels)
            values (%s,%s,%s,%s::jsonb)
            returning *
            """,(sender_id,media_id,analysis,psycopg2.extras.Json(labels or [])))
            row=dict(cur.fetchone())
        conn.commit()
    return {"ok": True, "analysis": row}

def get_last_visual_analysis(sender_id: str) -> dict:
    ensure_visual_schema()
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            select a.*, m.media_url, m.media_type
            from neura_visual_analysis a
            left join neura_visual_memory m on m.id=a.media_id
            where a.sender_id=%s
            order by a.created_at desc
            limit 1
            """,(sender_id,))
            row=cur.fetchone()
    return {"ok": True, "analysis": dict(row) if row else None}

def visual_followup_context(sender_id: str) -> dict:
    media=get_last_visual_media(sender_id).get("media")
    analysis=get_last_visual_analysis(sender_id).get("analysis")
    return {
        "ok": True,
        "has_media": bool(media),
        "has_analysis": bool(analysis),
        "media": media,
        "analysis": analysis
    }
