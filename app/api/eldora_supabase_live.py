import os, psycopg
from fastapi import APIRouter, HTTPException, Header

router = APIRouter(prefix="/eldora/supabase-live", tags=["eldora-supabase-live"])

SCHEMA_SQL = """
create table if not exists eldora_events (
  id bigserial primary key,
  tenant_id text,
  user_id text,
  event_type text not null,
  payload jsonb default '{}'::jsonb,
  idempotency_key text unique,
  created_at timestamptz default now()
);
"""

def _db():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise HTTPException(500, "DATABASE_URL missing")
    return psycopg.connect(url)

def _guard(token):
    expected = os.getenv("ADMIN_ACTIVATION_TOKEN")
    if expected and token != expected:
        raise HTTPException(403, "admin token invalid")
    return True

@router.post("/schema/apply")
def apply_schema(x_admin_token: str | None = Header(default=None)):
    _guard(x_admin_token)
    with _db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
        conn.commit()
    return {"schema_applied": True, "table": "eldora_events"}

@router.post("/event/insert-read")
def insert_read(payload: dict, x_admin_token: str | None = Header(default=None)):
    _guard(x_admin_token)
    key = payload.get("idempotency_key", "live-gate-key")
    with _db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """insert into eldora_events(tenant_id,user_id,event_type,payload,idempotency_key)
                   values(%s,%s,%s,%s,%s)
                   on conflict(idempotency_key) do update set payload=excluded.payload
                   returning id,event_type,idempotency_key""",
                (payload.get("tenant_id"), payload.get("user_id"), payload.get("event_type"), psycopg.types.json.Jsonb(payload.get("payload", {})), key)
            )
            row = cur.fetchone()
        conn.commit()
    return {"insert_read_ok": True, "id": row[0], "event_type": row[1], "idempotency_key": row[2]}
