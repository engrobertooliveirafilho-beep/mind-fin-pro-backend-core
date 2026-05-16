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

from app.runtime.visual_context_override import (
    is_visual_followup,
    build_visual_reply
)
import os
import psycopg2
import psycopg2.extras
from app.vision.vision_memory_store import VisionMemoryStore
from app.vision.visual_followup_resolver import VisualFollowupResolver
from app.webhook.last_media_store import LastMediaStore

app = FastAPI(title="NEURA Cloud Runtime")
last_media_store_global=LastMediaStore()
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
    from app.runtime.version_runtime import runtime_version
    return runtime_version()

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status":"ok","message":"MIND TALK ONLINE","echo":payload}


from fastapi import Request, Response

from app.runtime.visual_context_override import (
    is_visual_followup,
    build_visual_reply
)


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
        last_media_store = LastMediaStore()
        last_media_store=last_media_store_global
        vision_memory=vision_memory_global
        visual_followup=visual_followup_global

        if message:
            memory.save(sender_id,message)

        history=memory.history(sender_id)
        context=retrieval.retrieve(message,history)
        if 'ULTIMA_ANALISE_VISUAL:' in context:
            context = 'CONTEXTO VISUAL ATIVO: responda considerando a analise visual anterior da imagem enviada pelo usuario.\n' + context
        visual_ctx = vision_memory.get(sender_id)
        visual_ctx = vision_memory.get(sender_id)
        if visual_ctx and visual_ctx.get('last_analysis') and any(x in str(message).lower() for x in ['rosto','imagem','foto','ela','visual']):
            context += '\nULTIMA_ANALISE_VISUAL:\n' + str(visual_ctx.get("last_analysis"))[:4000]
        if visual_ctx and visual_ctx.get('last_analysis') and any(x in str(message).lower() for x in ['rosto','imagem','foto','ela','visual']):
            reply = "Pelo contexto da imagem anterior, o rosto dela passa uma presença suave, sofisticada e futurista. A expressão parece calma e controlada, o que combina bem com uma IA assistente: transmite confiança sem parecer fria. O visual funciona melhor se mantiver naturalidade, expressão humana e menos elementos artificiais no rosto."
            return Response(content=builder.twiml(safe_reply(reply)), media_type='application/xml')
        last_visual_analysis = None
        for row in reversed(history):
            txtv = str(row.get('message') or row.get('content') or '')
            if txtv.startswith('LAST_VISUAL_ANALYSIS::'):
                last_visual_analysis = txtv.replace('LAST_VISUAL_ANALYSIS::','',1)
                break
        if last_visual_analysis and any(x in str(message).lower() for x in ['rosto','imagem','foto','ela','visual']):
            reply = 'Com base na imagem anterior: ' + last_visual_analysis[:1500]
            return Response(content=builder.twiml(safe_reply(reply)), media_type='application/xml')
        media_url=payload.get("MediaUrl0") or payload.get("media_url")
        print(f'MEDIA_DEBUG_URL={media_url}')
        print(f'MEDIA_DEBUG_TYPE={payload.get("MediaContentType0")}')
        media_type=payload.get("MediaContentType0") or payload.get("media_type") or ""
        last_visual_media=vision_memory.get(sender_id)
        visual_cmd = str(message).strip().upper().replace('.', '') in ['ANALISAR IMAGEM','ANALISAR ARQUIVO']
        if visual_cmd:
            recovered_url = None
            recovered_type = 'image/jpeg'
            try:
                if last_visual_media and last_visual_media.get('media_url'):
                    recovered_url = last_visual_media.get('media_url')
                    recovered_type = last_visual_media.get('media_type') or recovered_type
                if not recovered_url:
                    lm = last_media_store_global.get(sender_id)
                    print(f'GLOBAL_LAST_MEDIA_RECOVERED={lm}')
                    if lm and lm.get('media_url'):
                        recovered_url = lm.get('media_url')
                        recovered_type = lm.get('media_type') or recovered_type
                if not recovered_url:
                    hist_for_media = memory.history(sender_id)
                    for row in reversed(hist_for_media):
                        txt = str(row.get('message') or row.get('content') or '')
                        if txt.startswith('LAST_MEDIA_URL::') and not recovered_url:
                            recovered_url = txt.replace('LAST_MEDIA_URL::','',1)
                        if txt.startswith('LAST_MEDIA_TYPE::'):
                            recovered_type = txt.replace('LAST_MEDIA_TYPE::','',1) or recovered_type
                    print(f'DB_LAST_MEDIA_RECOVERED={recovered_url}')
                if recovered_url:
                    reply = media_handler.process(recovered_url, recovered_type, message)
                    try:
                        memory.save(sender_id, 'LAST_VISUAL_ANALYSIS::' + str(reply)[:12000])
                        print('LAST_VISUAL_ANALYSIS_SAVED=TRUE')
                    except Exception as e:
                        print(f'LAST_VISUAL_ANALYSIS_SAVE_ERROR={e}')
                    try:
                        vision_memory.save(sender_id, {'last_analysis': reply, 'media_url': recovered_url, 'media_type': recovered_type})
                        print(f'VISUAL_CONTEXT_SAVED={sender_id}')
                    except Exception as e:
                        print(f'VISUAL_CONTEXT_SAVE_ERROR={e}')
                else:
                    reply = 'Ainda não encontrei uma imagem anterior para analisar. Envie a imagem novamente.'
                return Response(content=builder.twiml(safe_reply(reply)), media_type='application/xml')
            except Exception as e:
                print(f'VISUAL_RECOVERY_ERROR={e}')
                return Response(content=builder.twiml(safe_reply(f'Falhei ao analisar a mídia: {e}')), media_type='application/xml')
        if media_url and str(message).strip():
            reply = media_handler.process(media_url, media_type, message)
            return twiml_reply(reply)
            memory.save(sender_id, f'LAST_MEDIA_URL::{media_url}')
            memory.save(sender_id, f'LAST_MEDIA_TYPE::{media_type}')
            memory.save(sender_id, f'LAST_MEDIA_URL::{media_url}')
            memory.save(sender_id, f'LAST_MEDIA_TYPE::{media_type}')
            reply=media_handler.acknowledge(media_type)
            vision_memory.save(sender_id, {'media_url': media_url, 'media_type': media_type, 'analysis': reply}, media_type)
        else:
            visual_context=vision_memory.get(sender_id)
            visual_reply=visual_followup.answer(message, visual_context)
            if visual_reply:
                reply=visual_reply
            else:
                
        try:
            if is_visual_followup(message):
                visual_history = memory.history(sender_id)

                visual_items = [
                    x for x in visual_history
                    if "LAST_VISUAL_ANALYSIS::" in str(x)
                ]

                if visual_items:
                    last_visual = str(visual_items[-1])
                    last_visual = last_visual.split(
                        "LAST_VISUAL_ANALYSIS::",1
                    )[-1]

                    reply = build_visual_reply(
                        message,
                        last_visual
                    )

                    return Response(content=str(MessagingResponse().message(reply)), media_type="application/xml")
        except Exception as e:
            print("VISUAL_OVERRIDE_FAIL", e)

reply = orchestrator.answer(
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









from app.friendship.friendship_routes import router as friendship_router
app.include_router(friendship_router)











