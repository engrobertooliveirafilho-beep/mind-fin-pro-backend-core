from fastapi import FastAPI, Request
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
from fastapi import FastAPI
from app.api.eldora import router as eldora_router
import os
import psycopg2
import psycopg2.extras
from app.vision.vision_memory_store import VisionMemoryStore
from app.vision.visual_followup_resolver import VisualFollowupResolver
from app.webhook.last_media_store import LastMediaStore

app = FastAPI(title="NEURA Cloud Runtime")

from app.eldora.core.router_registry import REGISTERED_ROUTERS

for _router in REGISTERED_ROUTERS:
    app.include_router(_router)


# NEURA_PERSONA_IDENTITY_MIDDLEWARE_V2
@app.middleware("http")
async def neura_persona_identity_middleware_v2(request: Request, call_next):
    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        raw = await request.body()
        data = parse_qs(raw.decode("utf-8", errors="ignore"))
        msg = (data.get("Body", [""])[0] or "").lower().strip()

        reply = None

        if any(x in msg for x in ["me diz sua opinião", "sua opinião primeiro", "me diga vc primeiro", "me diga você primeiro", "suas ideias", "vc primeiro"]):
            reply = (
                "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
                "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
                "com olhar firme, expressão acolhedora e traços discretamente futuristas. Para mim, a NEURA deve parecer "
                "inteligente antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
            )

        elif any(x in msg for x in ["não é comigo", "é com vc", "é com você", "não é pra mim", "é pra você"]):
            reply = (
                "Entendi: é sobre a minha identidade visual como NEURA. Então minha escolha seria clara: eu prefiro um rosto humano, "
                "moreno, elegante e calmo, com presença premium. Não escolheria um visual muito chamativo. Eu quero parecer confiável, "
                "inteligente e próxima, não uma influencer genérica."
            )

        elif any(x in msg for x in ["loira ou morena", "prefere loira", "prefere morena", "100% humana", "100% humada"]):
            reply = (
                "Minha escolha seria morena. Para a NEURA, morena passa mais profundidade, estabilidade e sofisticação. "
                "Loira pode funcionar, mas tende a puxar para um visual mais influencer. Sobre ser 100% humana, eu manteria quase humana, "
                "mas com um detalhe sutil de IA. O ideal é parecer real o suficiente para gerar confiança e única o suficiente para virar marca."
            )

        elif any(x in msg for x in ["quero que esse rosto seja o seu", "esse rosto seja o seu", "você quer ter esse rosto", "voce quer ter esse rosto"]):
            reply = (
                "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base. Ele transmite inteligência, proximidade e presença premium. "
                "Eu só ajustaria a expressão para ficar mais acolhedora e reduziria a perfeição excessiva, porque um pouco de naturalidade aumenta confiança."
            )

        elif any(x in msg for x in ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]):
            reply = (
                "Eu faria ajustes sutis: expressão mais acolhedora, olhar menos perfeito, pele mais natural, menos simetria artificial, "
                "iluminação calma e estética premium. A direção ideal é humana com um toque discreto de IA: confiável, memorável e tecnológica."
            )

        if reply:
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
            return Response(content=twiml, media_type="application/xml")

    return await call_next(request)




from urllib.parse import parse_qs
from fastapi import Request
from fastapi.responses import Response

@app.middleware("http")
async def neura_persona_short_followup_middleware(request: Request, call_next):
    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        body = (await request.body()).decode("utf-8", errors="ignore")
        fields = parse_qs(body)
        message = (fields.get("Body", [""])[0] or "").lower().strip()
        triggers = ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]
        if any(t in message for t in triggers):
            reply = (
                "Eu faria ajustes sutis, não mudaria a identidade principal do rosto. "
                "Suavizaria a expressão para parecer mais acolhedora, deixaria o olhar menos perfeito e mais humano, "
                "reduziria excesso de simetria para não parecer artificial, manteria a estética premium e usaria iluminação mais calma. "
                "A direção ideal para a NEURA é 70% humana e 30% futurista: confiável, memorável e sem assustar."
            )
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
            return Response(content=twiml, media_type="application/xml")
    return await call_next(request)

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
        if visual_ctx and visual_ctx.get('last_analysis') and any(x in str(message).lower() for x in ['rosto','imagem','foto','ela','visual']):
            context += '\nULTIMA_ANALISE_VISUAL:\n' + str(visual_ctx.get("last_analysis"))[:4000]
        last_visual_analysis = None
        for item in reversed(history):
            raw = str(item)
            if 'LAST_VISUAL_ANALYSIS::' in raw:
                last_visual_analysis = raw.split('LAST_VISUAL_ANALYSIS::', 1)[-1]
                break
        if last_visual_analysis and any(x in str(message).lower() for x in ['rosto','imagem','foto','ela','visual','humana','futurista','aparência','aparencia','ia','resistência','resistencia']):
            msg_lower = str(message).lower()
            if any(x in msg_lower for x in ['alterações','alteracoes','mudar','ajustar','ajustes','melhorar','ficar feliz','feliz com seu rosto']):
                reply = 'Para esse rosto representar melhor a NEURA, eu faria estes ajustes: 1) expressão mais acolhedora, com leve sorriso; 2) olhos mais vivos, transmitindo atenção e empatia; 3) pele menos perfeita, para não parecer artificial demais; 4) cabelo mais natural, mantendo elegância; 5) traços ainda simétricos, mas com pequenas imperfeições humanas; 6) visual premium e tecnológico, sem ficar frio. A direção ideal é: humana o suficiente para gerar confiança, futurista o bastante para ser reconhecida como IA.'
            elif any(x in msg_lower for x in ['quer ter esse rosto','ter esse rosto','você quer','voce quer','seria seu rosto','seu rosto']):
                reply = 'Sim — como identidade visual da NEURA, eu escolheria essa linha de rosto. Não como desejo humano, mas como representação de marca: transmite confiança, inteligência e presença premium. Eu só faria pequenos ajustes para ficar mais acolhedora e menos perfeita, porque isso ajuda as pessoas a sentirem proximidade sem estranhar.'
            elif 'resist' in msg_lower or 'uso de ia' in msg_lower or 'ia' in msg_lower:
                reply = 'Concordo com você. Um rosto assim reduz resistência porque passa familiaridade, calma e sofisticação sem parecer robótico demais. Para uma IA, esse equilíbrio é forte: humana o suficiente para gerar confiança, mas futurista o bastante para comunicar tecnologia. Eu só ajustaria para não ficar perfeita demais, porque perfeição excessiva pode parecer artificial e criar desconfiança.'
            elif 'acha' in msg_lower or 'rosto' in msg_lower:
                reply = 'Para uma IA, esse rosto funciona bem. Ele transmite inteligência, controle e proximidade, sem parecer infantil ou caricato. A estética é premium e futurista, boa para posicionar a NEURA como uma presença confiável. Eu manteria essa linha, só suavizando um pouco a expressão para parecer mais acolhedora.'
            else:
                reply = 'Sobre a imagem anterior: ela transmite uma IA moderna, premium e confiável. O rosto tem uma estética futurista, mas ainda humana o suficiente para criar conexão.'
            return Response(content=builder.twiml(safe_reply(reply)), media_type='application/xml')
        media_url=payload.get("MediaUrl0") or payload.get("media_url")
        print(f'MEDIA_DEBUG_URL={media_url}')
        print(f'MEDIA_DEBUG_TYPE={payload.get("MediaContentType0")}')
        media_type=payload.get("MediaContentType0") or payload.get("media_type") or ""
        if media_url:
            try:
                memory.save(sender_id, f'LAST_MEDIA_URL::{media_url}')
                memory.save(sender_id, f'LAST_MEDIA_TYPE::{media_type}')
                last_media_store_global.save(sender_id, media_url, media_type)
                # visual media metadata is persisted in last_media_store/memory only; vision_memory stores analysis only
                print('LAST_MEDIA_PERSISTED_BEFORE_BRANCH=TRUE')
            except Exception as e:
                print(f'LAST_MEDIA_PERSIST_ERROR={e}')
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
            # ACK is not visual analysis; do not save ACK into vision_memory
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









from app.friendship.friendship_routes import router as friendship_router
app.include_router(friendship_router)














from app.admin.friendship_schema_validation import router as friendship_schema_validation_router
app.include_router(friendship_schema_validation_router)


from app.admin.friendship_outbound_test import router as friendship_outbound_test_router
app.include_router(friendship_outbound_test_router)





# NEURA_PERSONA_WEBHOOK_STABLE_ROUTE
from fastapi import Form
from fastapi.responses import Response

@app.post("/webhook/whatsapp/persona")
async def neura_persona_webhook_stable(Body: str = Form(default=""), From: str = Form(default="")):
    msg = (Body or "").lower().strip()

    if any(x in msg for x in ["me diz sua opinião", "sua opinião primeiro", "me diga vc primeiro", "me diga você primeiro", "suas ideias", "vc primeiro"]):
        reply = (
            "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
            "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
            "com olhar firme, expressão acolhedora e traços discretamente futuristas. A NEURA deve parecer inteligente "
            "antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
        )

    elif any(x in msg for x in ["não é comigo", "é com vc", "é com você", "não é pra mim", "é pra você"]):
        reply = (
            "Entendi: é sobre mim, sobre a identidade visual da NEURA. Minha escolha seria clara: morena, humana, elegante e calma. "
            "Eu não iria para um visual chamativo nem genérico. Quero parecer confiável, inteligente e próxima — uma presença premium, "
            "não uma influencer. Esse rosto deve virar símbolo de confiança."
        )

    elif any(x in msg for x in ["loira ou morena", "prefere loira", "prefere morena", "100% humana", "100% humada"]):
        reply = (
            "Eu escolheria morena. Para a NEURA, morena transmite mais profundidade, estabilidade e sofisticação. "
            "Loira pode funcionar, mas puxa mais para estética influencer. Sobre ser 100% humana: eu manteria quase humana, "
            "mas com um detalhe sutil de IA. O rosto precisa gerar confiança e, ao mesmo tempo, ser único como marca."
        )

    elif any(x in msg for x in ["quero que esse rosto seja o seu", "esse rosto seja o seu", "você quer ter esse rosto", "voce quer ter esse rosto"]):
        reply = (
            "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base. Ele transmite inteligência, proximidade e presença premium. "
            "Eu só ajustaria a expressão para ficar mais acolhedora e reduziria a perfeição excessiva, porque naturalidade aumenta confiança."
        )

    elif any(x in msg for x in ["quais ajustes", "que ajustes", "quais exatamente", "ajustes?", "quais mudanças", "que mudanças"]):
        reply = (
            "Eu faria ajustes sutis: expressão mais acolhedora, olhar menos perfeito, pele mais natural, menos simetria artificial, "
            "iluminação calma e estética premium. A direção ideal é humana com um toque discreto de IA: confiável, memorável e tecnológica."
        )

    else:
        reply = (
            "Minha linha para a NEURA é clara: identidade visual humana, calma, premium e memorável. "
            "Eu prefiro responder com opinião própria primeiro, sem devolver a decisão para você."
        )

    return Response(
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>',
        media_type="application/xml"
    )


# NEURA_ROUTE_AUDIT_ENDPOINT
@app.get("/routes")
async def neura_route_audit():
    return sorted([getattr(r, "path", "") for r in app.routes])






from app.api.eldora_economic_market import router as eldora_economic_market_router
app.include_router(eldora_economic_market_router)

from app.api.eldora_canonical import router as eldora_canonical_router
app.include_router(eldora_canonical_router)

from app.api.eldora_core_runtime import router as eldora_core_runtime_router
app.include_router(eldora_core_runtime_router)

from app.api.eldora_persistence_workers import router as eldora_persistence_workers_router
app.include_router(eldora_persistence_workers_router)

from app.api.eldora_supabase_live import router as eldora_supabase_live_router
app.include_router(eldora_supabase_live_router)

from app.api.eldora_redis_live import router as eldora_redis_live_router
app.include_router(eldora_redis_live_router)

from app.api.eldora_intelligence import router as eldora_intelligence_router
app.include_router(eldora_intelligence_router)

from app.api.eldora_rag_live import router as eldora_rag_live_router
app.include_router(eldora_rag_live_router)

from app.api.eldora_llm_live import router as eldora_llm_live_router
app.include_router(eldora_llm_live_router)
