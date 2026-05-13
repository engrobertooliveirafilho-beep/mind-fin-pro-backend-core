from fastapi import FastAPI
import os
import psycopg2
import psycopg2.extras

app = FastAPI(title="NEURA Cloud Runtime")

DATABASE_URL = os.getenv("DATABASE_URL")
LAST_TABLE_ERROR = None
LAST_INSERT_ERROR = None
LAST_FETCH_ERROR = None

def db_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL_MISSING")
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def ensure_table():
    global LAST_TABLE_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS neura_memory (
                    id BIGSERIAL PRIMARY KEY,
                    sender_id TEXT,
                    role TEXT DEFAULT 'conversation',
                    content TEXT,
                    confidence DOUBLE PRECISION DEFAULT 0.8,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    message TEXT
                );
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS sender_id TEXT;
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'conversation';
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS content TEXT;
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION DEFAULT 0.8;
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
                ALTER TABLE neura_memory ADD COLUMN IF NOT EXISTS message TEXT;
                """)
        LAST_TABLE_ERROR = None
    except Exception as e:
        LAST_TABLE_ERROR = str(e)

ensure_table()

def memory_insert(sender_id, message):
    global LAST_INSERT_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO neura_memory(sender_id,role,content,confidence,message) VALUES (%s,%s,%s,%s,%s)",
                    (sender_id, "conversation", message, 0.8, message)
                )
        LAST_INSERT_ERROR = None
        return True
    except Exception as e:
        LAST_INSERT_ERROR = str(e)
        return False

def memory_fetch(sender_id):
    global LAST_FETCH_ERROR
    try:
        with db_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT id,sender_id,content,message,created_at FROM neura_memory WHERE sender_id=%s ORDER BY created_at ASC LIMIT 50",
                    (sender_id,)
                )
                rows = cur.fetchall()
        LAST_FETCH_ERROR = None
        return [dict(r) for r in rows]
    except Exception as e:
        LAST_FETCH_ERROR = str(e)
        return []

def text_of(row):
    return (row.get("message") or row.get("content") or "")

def answer(message, history):
    lower = message.lower()
    if "qual é meu nome" in lower or "qual e meu nome" in lower:
        for h in history:
            m = text_of(h)
            if "meu nome é" in m.lower():
                return m.split("é",1)[-1].strip()
    if "o que estou estudando" in lower:
        for h in history:
            m = text_of(h)
            if "estou estudando" in m.lower():
                return m
    if "quando é minha prova" in lower or "quando e minha prova" in lower:
        for h in history:
            m = text_of(h)
            if "prova" in m.lower():
                return m
    return "NEURA WEBHOOK ONLINE"

@app.get("/health")
def health():
    return {"status":"ok","service":"mind-fin-pro-backend"}

@app.get("/health/env")
def health_env():
    return {
        "database_url": bool(DATABASE_URL),
        "table_error": LAST_TABLE_ERROR,
        "insert_error": LAST_INSERT_ERROR,
        "fetch_error": LAST_FETCH_ERROR
    }

@app.get("/version")
def version():
    return {"commit":"080f027-parser-twilio-active","runtime":"postgres_memory_runtime_v4_twilio_parser"}

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status":"ok","message":"MIND TALK ONLINE","echo":payload}


from fastapi import Request

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):

    payload = {}

    try:
        ctype = request.headers.get("content-type","")

        if "application/json" in ctype:
            payload = await request.json()
        else:
            form = await request.form()
            payload = dict(form)

    except Exception as e:
        payload = {"parser_error": str(e)}

    sender_id = (
        payload.get("From")
        or payload.get("from")
        or payload.get("sender_id")
        or "unknown"
    )

    message = (
        payload.get("Body")
        or payload.get("body")
        or payload.get("message")
        or ""
    )

    return {
        "status":"ok",
        "sender_id":sender_id,
        "message":message,
        "payload":payload
    }
