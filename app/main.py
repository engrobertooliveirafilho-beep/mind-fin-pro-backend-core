from fastapi import FastAPI
from datetime import datetime
import os
import psycopg2
import psycopg2.extras

app = FastAPI(title="NEURA Cloud Runtime")

DATABASE_URL = os.getenv("DATABASE_URL")
LAST_DB_ERROR = None

def db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_MISSING")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def ensure_table():
    global LAST_DB_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS neura_memory (
                    id BIGSERIAL PRIMARY KEY,
                    sender_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """)
        LAST_DB_ERROR = None
        print("NEURA_MEMORY_TABLE_READY")
    except Exception as e:
        LAST_DB_ERROR = str(e)
        print("NEURA_MEMORY_TABLE_ERROR:", LAST_DB_ERROR)

ensure_table()

def memory_insert(sender_id, message):
    global LAST_DB_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO neura_memory(sender_id,message) VALUES (%s,%s)",
                    (sender_id, message)
                )
        LAST_DB_ERROR = None
        return True
    except Exception as e:
        LAST_DB_ERROR = str(e)
        print("MEMORY_INSERT_ERROR:", LAST_DB_ERROR)
        return False

def memory_fetch(sender_id):
    global LAST_DB_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id,sender_id,message,created_at FROM neura_memory WHERE sender_id=%s ORDER BY id ASC LIMIT 50",
                    (sender_id,)
                )
                rows = cur.fetchall()
        LAST_DB_ERROR = None
        return [dict(r) for r in rows]
    except Exception as e:
        LAST_DB_ERROR = str(e)
        print("MEMORY_FETCH_ERROR:", LAST_DB_ERROR)
        return []

def answer(message, history):
    lower = message.lower()
    if "qual é meu nome" in lower or "qual e meu nome" in lower:
        for h in history:
            m = h.get("message","")
            if "meu nome é" in m.lower():
                return m.split("é",1)[-1].strip()
    if "o que estou estudando" in lower:
        for h in history:
            m = h.get("message","")
            if "estou estudando" in m.lower():
                return m
    if "quando é minha prova" in lower or "quando e minha prova" in lower:
        for h in history:
            m = h.get("message","")
            if "prova" in m.lower():
                return m
    return "NEURA WEBHOOK ONLINE"

@app.get("/health")
def health():
    return {"status":"ok","service":"mind-fin-pro-backend"}

@app.get("/health/env")
def health_env():
    return {"database_url": bool(DATABASE_URL), "last_db_error": LAST_DB_ERROR}

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status":"ok","message":"MIND TALK ONLINE","echo":payload}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(payload: dict):
    sender_id = payload.get("sender_id","unknown")
    message = payload.get("message","")
    inserted = memory_insert(sender_id, message)
    history = memory_fetch(sender_id)
    response = answer(message, history)
    return {
        "status":"ok",
        "response":response,
        "inserted":inserted,
        "history_count":len(history),
        "last_db_error":LAST_DB_ERROR,
        "echo":payload
    }

@app.get("/version")
def version():
    return {
        "commit": "09d6455",
        "runtime": "postgres_memory_runtime"
    }

