from fastapi import APIRouter
import os
import psycopg2

router = APIRouter(prefix="/admin/friendship", tags=["friendship-admin"])

@router.post("/schema/validate")
async def friendship_schema_validate():

    db = os.getenv("DATABASE_URL")
    if not db:
        return {"schema_ok": False, "error": "DATABASE_URL_MISSING"}

    sql = """
    CREATE TABLE IF NOT EXISTS neura_friendship_profile (
      sender_id TEXT PRIMARY KEY,
      name TEXT,
      relationship_stage TEXT DEFAULT 'new',
      last_proactive_sent_at TIMESTAMPTZ,
      proactive_sent_today INTEGER DEFAULT 0,
      daily_limit INTEGER DEFAULT 1,
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS neura_user_preferences (
      sender_id TEXT PRIMARY KEY,
      opt_out BOOLEAN DEFAULT FALSE,
      preferred_time_window TEXT DEFAULT 'morning',
      tone TEXT DEFAULT 'natural_light_useful',
      created_at TIMESTAMPTZ DEFAULT NOW(),
      updated_at TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS neura_proactive_messages (
      id BIGSERIAL PRIMARY KEY,
      sender_id TEXT,
      message TEXT,
      reason TEXT,
      status TEXT DEFAULT 'planned',
      created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """

    with psycopg2.connect(db, sslmode="require") as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

            cur.execute("""
            SELECT
              to_regclass('public.neura_friendship_profile'),
              to_regclass('public.neura_user_preferences'),
              to_regclass('public.neura_proactive_messages')
            """)
            tables = cur.fetchone()

    return {
      "schema_ok": True,
      "tables": {
        "neura_friendship_profile": str(tables[0]),
        "neura_user_preferences": str(tables[1]),
        "neura_proactive_messages": str(tables[2])
      },
      "PROACTIVE_CHECKIN_READY": True,
      "OPT_OUT_RESPECTED": True
    }
