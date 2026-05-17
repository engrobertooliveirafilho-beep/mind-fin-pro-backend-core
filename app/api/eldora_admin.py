import os
import psycopg2
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/eldora/admin", tags=["eldora-admin"])

SCHEMA_SQL = """
create table if not exists eldora_audit_events (
    id bigserial primary key,
    event_type text not null,
    actor text default 'system',
    payload jsonb default '{}'::jsonb,
    created_at timestamptz default now()
);

create table if not exists eldora_event_store (
    id bigserial primary key,
    topic text not null,
    payload jsonb default '{}'::jsonb,
    created_at timestamptz default now()
);
"""

@router.post("/apply-schema")
async def apply_schema(x_admin_token: str = Header(default="")):
    expected = os.getenv("ELDORA_ADMIN_TOKEN", "")
    if not expected or x_admin_token != expected:
        raise HTTPException(status_code=403, detail="forbidden")

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL missing")

    conn = psycopg2.connect(database_url)
    with conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
    conn.close()

    return {"status": "ok", "schema_applied": True}
