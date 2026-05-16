# disabled missing module neura_viral_router
from app.medical_curriculum.routes import router as medical_curriculum_router
from app.auto_ingestion.routes import router as auto_ingestion_router
from app.medical_research.routes import router as medical_research_router
from app.medical_swarm.validation_routes import router as medical_validation_router
from app.medical_swarm.routes import router as medical_swarm_router
from app.admin.env_audit import router as env_audit_router
from app.multi_llm.provider_routes import router as provider_routes_router
from app.multi_llm.live_routes import router as multi_llm_live_router
from app.multi_llm.routes import router as multi_llm_router
from app.memory.provider import MemoryProvider
from app.retrieval.provider import RetrievalProvider
from app.orchestrator.prompt_orchestrator import PromptOrchestrator
from app.runtime.response_builder import ResponseBuilder
from fastapi import FastAPI, Request, Response
import os
import psycopg2
import psycopg2.extras
from app.vision.vision_memory_store import VisionMemoryStore
from app.vision.visual_followup_resolver import VisualFollowupResolver

app = FastAPI(title="NEURA Cloud Runtime")
vision_memory_global=VisionMemoryStore()
visual_followup_global=VisualFollowupResolver()

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
    return {"commit":"1997cf6","runtime":"semantic_runtime_build"}

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status":"ok","message":"MIND TALK ONLINE","echo":payload}


from fastapi import Request, Response


def safe_reply(value):
    text = str(value or '').strip()
    text = text.replace('&', 'e')
    text = text.replace('<', '')
    text = text.replace('>', '')
    print(f'TWIML_REPLY_LEN={len(text)}')
    if len(text) > 900:
        text = text[:900] + '... Digite APROFUNDAR para continuar.'
    if not text:
        text = 'Recebi sua mensagem, mas não consegui gerar uma resposta agora.'
    return text

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    from app.runtime.response_builder import ResponseBuilder
    builder=ResponseBuilder()

    try:
        ctype=request.headers.get("content-type","")
        if "application/json" in ctype:
            payload=await request.json()
        else:
            form=await request.form()
            payload=dict(form)

        sender_id=payload.get("From") or payload.get("from") or payload.get("sender_id") or "unknown"
        message=payload.get("Body") or payload.get("body") or payload.get("message") or ""

        from app.memory.provider import MemoryProvider
        from app.retrieval.provider import RetrievalProvider
        from app.orchestrator.prompt_orchestrator import PromptOrchestrator
        from app.webhook.media_handler import MediaHandler

        memory=MemoryProvider()
        retrieval=RetrievalProvider()
        orchestrator=PromptOrchestrator()
        media_handler=MediaHandler()
        vision_memory=vision_memory_global
        visual_followup=visual_followup_global

        if message:
            memory.save(sender_id,message)

        history=memory.history(sender_id)
        context=retrieval.retrieve(message,history)
        media_url=payload.get("MediaUrl0") or payload.get("media_url")
        print(f'MEDIA_DEBUG_URL={media_url}')
        print(f'MEDIA_DEBUG_TYPE={payload.get("MediaContentType0")}')
        media_type=payload.get("MediaContentType0") or payload.get("media_type") or ""
        last_visual_media=vision_memory.get(sender_id)
        if str(message).strip().upper().replace('.', '') in ['ANALISAR IMAGEM','ANALISAR ARQUIVO'] and last_visual_media:
            reply=media_handler.process(last_visual_media.get('media_url'), last_visual_media.get('media_type'), message)
            return Response(content=builder.twiml(safe_reply(reply)), media_type='application/xml')

        if media_url:
            reply=media_handler.process(media_url,media_type,message)
            vision_memory.save(sender_id, {'media_url': media_url, 'media_type': media_type, 'analysis': reply}, media_type)
        else:
            visual_context=vision_memory.get(sender_id)
            visual_reply=visual_followup.answer(message, visual_context)
            if visual_reply:
                reply=visual_reply
            else:
                reply=orchestrator.answer(
        message,
        memory_context=context.get("history_text",""),
        retrieved_context=context
    )

    except Exception as e:
        reply=f"WEBHOOK_ERROR_TOTAL: {type(e).__name__}: {str(e)[:180]}"

    return Response(content=builder.twiml(safe_reply(reply)), media_type="application/xml")

from app.admin.semantic_activation import router as semantic_activation_router
app.include_router(semantic_activation_router)



from app.admin.beta_platform import router as beta_platform_router
app.include_router(beta_platform_router)


from app.admin.public_runtime import router as public_runtime_router
app.include_router(public_runtime_router)


app.include_router(multi_llm_router)


app.include_router(multi_llm_live_router)


app.include_router(provider_routes_router)


app.include_router(env_audit_router)


app.include_router(medical_swarm_router)


app.include_router(medical_validation_router)


app.include_router(medical_research_router)


app.include_router(auto_ingestion_router)


app.include_router(medical_curriculum_router)









try:
    pass
    # disabled include_router neura_viral_router
except NameError:
    pass


# disabled neura whatsapp webhook router

try:
    pass
    # disabled include_router neura_whatsapp_router
except Exception as e:
    print(f"[NEURA_WEBHOOK_ROUTER_ERROR] {e}")






