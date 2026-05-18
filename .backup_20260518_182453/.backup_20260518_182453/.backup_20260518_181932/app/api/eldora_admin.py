import os
import psycopg2
from fastapi import APIRouter, Depends

from app.eldora.core.admin_guard import require_admin

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
async def apply_schema(_: bool = Depends(require_admin)):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"status": "error", "detail": "DATABASE_URL missing"}

    conn = psycopg2.connect(database_url)
    with conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
    conn.close()

    return {"status": "ok", "schema_applied": True}

PGVECTOR_SCHEMA_SQL = """
create extension if not exists vector;

create table if not exists eldora_cognitive_memory (
    id bigserial primary key,
    tenant_id text default 'default',
    user_ref text default 'anonymous',
    content text not null,
    category text default 'general',
    embedding vector(16),
    priority int default 1,
    created_at timestamptz default now()
);
"""

@router.post("/apply-pgvector-schema")
async def apply_pgvector_schema(_: bool = Depends(require_admin)):
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return {"status": "error", "detail": "DATABASE_URL missing"}

    conn = psycopg2.connect(database_url)
    with conn:
        with conn.cursor() as cur:
            cur.execute(PGVECTOR_SCHEMA_SQL)
    conn.close()

    return {"status": "ok", "pgvector_schema_applied": True}
