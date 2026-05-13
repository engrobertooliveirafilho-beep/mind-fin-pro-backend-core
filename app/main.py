from fastapi import FastAPI
from datetime import datetime
from supabase import create_client
import os
import psycopg2

app = FastAPI(title="NEURA Cloud Runtime")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def ensure_table():
    if not DATABASE_URL:
        print("DATABASE_URL_MISSING")
        return
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS neura_memory (
            id BIGSERIAL PRIMARY KEY,
            sender_id TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("NEURA_MEMORY_TABLE_READY")
    except Exception as e:
        print("NEURA_MEMORY_TABLE_ERROR:", str(e))

ensure_table()

def memory_insert(sender_id, message):
    if not supabase:
        print("SUPABASE_NOT_CONNECTED")
        return False
    try:
        supabase.table("neura_memory").insert({"sender_id": sender_id, "message": message}).execute()
        print("SUPABASE_INSERT_OK")
        return True
    except Exception as e:
        print("SUPABASE_INSERT_ERROR:", str(e))
        return False

def memory_fetch(sender_id):
    if not supabase:
        return []
    try:
        r = supabase.table("neura_memory").select("*").eq("sender_id", sender_id).order("id", desc=False).limit(50).execute()
        print("SUPABASE_FETCH_COUNT:", len(r.data or []))
        return r.data or []
    except Exception as e:
        print("SUPABASE_FETCH_ERROR:", str(e))
        return []

def answer(message, history):
    lower = message.lower()
    if "qual é meu nome" in lower or "qual e meu nome" in lower:
        for h in history:
            m = h.get("message", "")
            if "meu nome é" in m.lower():
                return m.split("é", 1)[-1].strip()
    if "o que estou estudando" in lower:
        for h in history:
            m = h.get("message", "")
            if "estou estudando" in m.lower():
                return m
    if "quando é minha prova" in lower or "quando e minha prova" in lower:
        for h in history:
            m = h.get("message", "")
            if "prova" in m.lower():
                return m
    return "NEURA WEBHOOK ONLINE"

@app.get("/health")
def health():
    return {"status": "ok", "service": "mind-fin-pro-backend"}

@app.get("/health/env")
def health_env():
    return {"supabase_url": bool(SUPABASE_URL), "service_role": bool(SUPABASE_KEY), "database_url": bool(DATABASE_URL)}

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status": "ok", "message": "MIND TALK ONLINE", "echo": payload}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict):
    sender_id = payload.get("sender_id", "unknown")
    message = payload.get("message", "")
    inserted = memory_insert(sender_id, message)
    history = memory_fetch(sender_id)
    response = answer(message, history)
    return {"status": "ok", "response": response, "inserted": inserted, "history_count": len(history), "echo": payload}
