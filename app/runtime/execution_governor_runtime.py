
import os
import uuid
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone

def _db():
    return os.getenv("DATABASE_URL")

SCHEMA = """
CREATE TABLE IF NOT EXISTS neura_execution_plans (
  plan_id TEXT PRIMARY KEY,
  sender_id TEXT NOT NULL,
  goal TEXT NOT NULL,
  steps JSONB NOT NULL,
  status TEXT DEFAULT 'planned',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS neura_execution_checkpoints (
  checkpoint_id TEXT PRIMARY KEY,
  sender_id TEXT NOT NULL,
  plan_id TEXT,
  runtime_state JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS neura_governor_events (
  id BIGSERIAL PRIMARY KEY,
  sender_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  amount INTEGER DEFAULT 1,
  allowed BOOLEAN DEFAULT TRUE,
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
"""

def ensure_execution_schema():
    if not _db():
        return {"ok": False, "error": "DATABASE_URL_MISSING"}
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA)
        conn.commit()
    return {"ok": True}

def create_execution_plan(sender_id: str, goal: str, steps: list[str] | None = None) -> dict:
    ensure_execution_schema()
    plan_id=str(uuid.uuid4())
    steps=steps or ["retrieve_context","rank_memory","decide_next_action","execute","record_evidence"]
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_execution_plans(plan_id,sender_id,goal,steps,status)
            values (%s,%s,%s,%s::jsonb,'planned')
            returning *
            """,(plan_id,sender_id,goal,psycopg2.extras.Json(steps)))
            row=dict(cur.fetchone())
        conn.commit()
    return {"ok": True, "plan": row}

def get_active_plans(sender_id: str, limit: int = 5) -> dict:
    ensure_execution_schema()
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            select * from neura_execution_plans
            where sender_id=%s and status in ('planned','active')
            order by created_at desc
            limit %s
            """,(sender_id,limit))
            rows=[dict(x) for x in cur.fetchall()]
    return {"ok": True, "plans": rows}

def create_execution_checkpoint(sender_id: str, runtime_state: dict, plan_id: str | None = None) -> dict:
    ensure_execution_schema()
    checkpoint_id=str(uuid.uuid4())
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            insert into neura_execution_checkpoints(checkpoint_id,sender_id,plan_id,runtime_state)
            values (%s,%s,%s,%s::jsonb)
            returning *
            """,(checkpoint_id,sender_id,plan_id,psycopg2.extras.Json(runtime_state or {})))
            row=dict(cur.fetchone())
        conn.commit()
    return {"ok": True, "checkpoint": row}

def governor_allow(sender_id: str, event_type: str = "runtime_step", amount: int = 1, daily_limit: int = 50) -> dict:
    ensure_execution_schema()
    with psycopg2.connect(_db(), sslmode="require") as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
            select coalesce(sum(amount),0)
            from neura_governor_events
            where sender_id=%s and created_at::date=now()::date and allowed=true
            """,(sender_id,))
            used=int(cur.fetchone()["coalesce"] or 0)
            allowed=(used + amount) <= daily_limit
            reason="ok" if allowed else "daily_governor_limit"
            cur.execute("""
            insert into neura_governor_events(sender_id,event_type,amount,allowed,reason)
            values (%s,%s,%s,%s,%s)
            returning *
            """,(sender_id,event_type,amount,allowed,reason))
            event=dict(cur.fetchone())
        conn.commit()
    return {"ok": True, "allowed": allowed, "used_before": used, "daily_limit": daily_limit, "event": event}
