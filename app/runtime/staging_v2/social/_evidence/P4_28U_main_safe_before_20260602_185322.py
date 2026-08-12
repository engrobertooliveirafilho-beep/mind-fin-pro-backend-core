
try:
    from app.runtime.ucce_canary_router import should_use_ucce, CANARY_ENABLED, CANARY_PERCENT, ALLOWLIST
    from app.runtime.ucce_canary_trace import trace_canary, get_last_canary_trace
    from app.runtime.ucce_shadow_mode import run_ucce_shadow
except Exception:
    should_use_ucce=None

try:
    from app.runtime.ucce_shadow_mode import run_ucce_shadow
    from app.runtime.ucce_decision_diff import compare_decisions
except Exception:
    run_ucce_shadow=None
    compare_decisions=None
from app.runtime.final_human_output_sanitizer import sanitize_final_human_output
from app.runtime.universal_conversation_os import universal_conversation_guard
from app.runtime.actionable_continuity_authority import set_actionable_turn_context, guard_actionable_reply, resolve_actionable_followup, detect_intent
# P4_12N_MAIN_INTERCEPTOR_TRACE

# P4_12N_MAIN_WEBHOOK_TRACE
from app.runtime.forensic_trace import event

# P4_12N_FORENSIC_BOOTSTRAP_ACTIVE
try:
    from app.runtime.forensic_trace import event
    event("FORENSIC_BOOTSTRAP_ACTIVE", module_name="app.main")
except Exception as _e:
    print("FORENSIC_BOOTSTRAP_FAIL", repr(_e))


# P4.12N forensic observability only: no cognitive guard, no reply mutation
try:
    from app.runtime import forensic_bootstrap
    forensic_bootstrap.install()
except Exception as _mind_forensic_error:
    print('MIND_FORENSIC_BOOTSTRAP_ERROR', repr(_mind_forensic_error))

from app.runtime.whatsapp_trace_sensor import sanitize_final_output

from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.runtime.single_runtime_dispatcher import dispatch_single_runtime
from app.runtime.final_conversational_arbiter import final_conversational_arbiter


# P4_28T_REMOTE_TRACE_BUFFER
_P428S_TRACE_BUFFER = []

# P4_28S_LIVE_WEBHOOK_TRACE
def _p428s_trace(stage: str, payload: dict):
    try:
        import json, pathlib, datetime
        global _P428S_TRACE_BUFFER
        event = {"ts": datetime.datetime.utcnow().isoformat(), "stage": stage, **payload}
        _P428S_TRACE_BUFFER.append(event)
        _P428S_TRACE_BUFFER = _P428S_TRACE_BUFFER[-100:]
        d = pathlib.Path("_evidence/P4_28S_LIVE_WEBHOOK_TRACE")
        d.mkdir(parents=True, exist_ok=True)
        with (d / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def twiml(message: str) -> str:
    safe = str(message).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
<Message>{sanitize_final_human_output(sanitize_final_human_output(safe))}</Message>
</Response>"""

from app.runtime.forensic_trace import new_trace,mark,fail,save
from fastapi import FastAPI, Request, Form
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
from app.runtime.cognitive_conversation_runtime import decide_turn
from fastapi import FastAPI, Form
from app.api.eldora import router as eldora_router
import os
import psycopg2
import psycopg2.extras
from app.vision.vision_memory_store import VisionMemoryStore
from app.vision.visual_followup_resolver import VisualFollowupResolver
from app.webhook.last_media_store import LastMediaStore

app = FastAPI(title="NEURA Cloud Runtime")


@app.middleware("http")
async def live_contract_middleware_patch(request, call_next):
    # LIVE_CONTRACT_MIDDLEWARE_PATCH
    event("MAIN_INTERCEPTOR_CHECK", route="/webhook/whatsapp", module_name="app.main")
    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        try:
            from urllib.parse import parse_qs
            body = (await request.body()).decode("utf-8", errors="ignore")
            fields = parse_qs(body)
            message = (fields.get("Body", [""])[0] or "").strip().lower()
            pass
            pass
        except Exception:
            pass
    return await call_next(request)
from app.eldora.core.router_registry import REGISTERED_ROUTERS

for _router in REGISTERED_ROUTERS:
    app.include_router(_router)


# NEURA_PERSONA_IDENTITY_MIDDLEWARE_V2
@app.middleware("http")
async def neura_persona_identity_middleware_v2(request: Request, call_next):
    event("MAIN_INTERCEPTOR_CHECK", route="/webhook/whatsapp", module_name="app.main")

    msg = ""
    reply = None

    if request.url.path == "/webhook/whatsapp" and request.method.upper() == "POST":
        raw = await request.body()
        data = parse_qs(raw.decode("utf-8", errors="ignore"))
        msg = (data.get("Body", [""])[0] or "").lower().strip()

        if any(x in msg for x in [
            "me diz sua opinião","sua opinião primeiro",
            "me diga vc primeiro","me diga você primeiro",
            "suas ideias","vc primeiro"
        ]):
            reply = (
                "Minha opinião direta: eu seguiria com esse rosto como base da identidade visual da NEURA, "
                "mas não deixaria com aparência genérica de modelo. Eu faria uma versão humana, calma e premium, "
                "com olhar firme, expressão acolhedora e traços discretamente futuristas. Para mim, a NEURA deve parecer "
                "inteligente antes de parecer bonita. A estética ideal é confiança, presença e memória visual."
            )

        elif any(x in msg for x in [
            "não é comigo","é com vc","é com você",
            "não é pra mim","é pra você"
        ]):
            reply = (
                "Entendi: é sobre a minha identidade visual como NEURA. Então minha escolha seria clara: "
                "eu prefiro um rosto humano, moreno, elegante e calmo, com presença premium."
            )

        elif any(x in msg for x in [
            "loira ou morena","prefere loira",
            "prefere morena","100% humana","100% humada"
        ]):
            reply = (
                "Minha escolha seria morena. Para a NEURA, morena passa profundidade, estabilidade e sofisticação."
            )

        elif any(x in msg for x in [
            "quero que esse rosto seja o seu",
            "esse rosto seja o seu",
            "você quer ter esse rosto",
            "voce quer ter esse rosto"
        ]):
            reply = (
                "Sim. Como identidade visual da NEURA, eu escolheria esse rosto como base."
            )

        elif any(x in msg for x in [
            "quais ajustes","que ajustes",
            "quais exatamente","ajustes?",
            "quais mudanças","que mudanças"
        ]):
            reply = (
                "Eu faria ajustes sutis: expressão mais acolhedora, pele mais natural, "
                "menos perfeição artificial e iluminação premium."
            )

        if reply:
            twiml = (
                '<?xml version="1.0" encoding="UTF-8"?>'
                f'<Response><Message>{sanitize_final_human_output(reply)}</Message></Response>'
            )
            event("MAIN_INTERCEPTOR_RETURN",
                  route="/webhook/whatsapp",
                  module_name="app.main")
            return Response(content=twiml, media_type="application/xml")

    return await call_next(request)




from urllib.parse import parse_qs
from fastapi import Request, Form
from fastapi.responses import Response
from app.api.whatsapp import eldora_primary_runtime_reply, twiml as primary_twiml
from app.runtime.p4_13g_router import route_natural_whatsapp
from app.runtime.semantic_whatsapp_runtime import route_semantic_whatsapp
from app.runtime.short_memory import remember, recall
from app.runtime.canary_gate import canary_allowed, semantic_enabled, log_canary
from app.runtime.factual_search_handoff import factual_search_handoff
from app.runtime.strategic_conversation_authority import strategic_conversation_authority
from app.runtime.whatsapp_final_output_guard import p4_12_whatsapp_live_ux_guard, p4_12_context_lock, p4_12b_factual_execution_lock

@app.middleware("http")
async def neura_persona_short_followup_middleware(request: Request, call_next):
    event("MAIN_INTERCEPTOR_CHECK", route="/webhook/whatsapp", module_name="app.main")
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
            twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(reply))}</Message></Response>'
            event("MAIN_INTERCEPTOR_RETURN", route="/webhook/whatsapp", module_name="app.main")
            return Response(content=_p412n_normalize_xml_response(message if "message" in locals() else "", twiml), media_type="application/xml")
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


@app.get("/ucce/canary-trace")
def ucce_canary_trace_route():
    try:
        return get_last_canary_trace()
    except Exception as e:
        return {"error": str(e)}
        
@app.get("/version")
def version():
    from app.runtime.version_runtime import runtime_version
    return runtime_version()

@app.post("/mind/talk")
async def mind_talk(payload: dict):
    return {"status":"ok","message":"MIND TALK ONLINE","echo":payload}


from fastapi import Request, Response, Form



def _apply_actionable_guard(reply, payload=None, message=""):
    try:
        data = payload or {}
        real_message = (
            str(message or "").strip()
            or str(data.get("Body") or "").strip()
            or str(data.get("body") or "").strip()
            or str(data.get("message") or "").strip()
        )
        sender = (
            str(data.get("From") or "").strip()
            or str(data.get("from") or "").strip()
            or str(data.get("sender_id") or "").strip()
        )
        return guard_actionable_reply(
            str(reply),
            sender_id=sender,
            user_message=real_message,
            last_state={}
        )
    except Exception:
        return reply

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


def _p412n_final_cognitive_safety(message: str, reply: str) -> str:
    decision = decide_turn(message)
    raw = str(reply or "")
    bad = ["Resumo /", "compatibility", "Compatibilidade:", "Memória contextual", "Memoria contextual"]
    if not decision.allow_factual_memory and any(x.lower() in raw.lower() for x in bad):
        if decision.turn_type == "SOCIAL_DIALOGUE":
            return "Oi, Roberto. Tudo certo."
        if decision.turn_type == "META_CONVERSATION":
            return "Para me deixar mais fluida, fale direto o objetivo e eu respondo sem puxar contexto antigo."
        if decision.turn_type == "RECOVERY":
            return "Entendi. Vou corrigir o rumo sem reaproveitar o contexto anterior."
        return "Entendi. Vou seguir pelo contexto atual sem reiniciar a conversa."
    return raw


# P4_12N_FINAL_FALLBACK_NORMALIZER
def _p412n_final_fallback_normalizer(message: str, reply: str) -> str:
    from app.runtime.cognitive_conversation_runtime import decide_turn
    decision=decide_turn(message)
    raw=str(reply or "").strip()
    bad=[
        "Eldora ativa","Tudo certo por aqui","Diagnóstico: o runtime identificou resposta fraca",
        "Resumo / compatibility","Compatibilidade:"
    ]
    if not raw or any(x.lower() in raw.lower() for x in bad):
        if decision.turn_type=="SOCIAL_DIALOGUE":
            return "Tudo certo, Roberto. Pode mandar."
        if decision.turn_type=="META_CONVERSATION":
            return "Para ficar mais fluida, me corrija no ponto exato e eu ajusto o tom na próxima resposta."
        if decision.turn_type=="FACTUAL_TASK":
            return "Entendi. Vou verificar isso com base no que você mandou e te responder direto."
        if decision.turn_type=="RECOVERY":
            return "Entendi. Vou corrigir o rumo sem puxar o contexto errado."
        return "Entendi. Vou seguir pelo contexto atual sem reiniciar a conversa."
    return raw


# P4_12N_XML_RESPONSE_NORMALIZER

def _p412n_response_quality_bad(reply: str) -> bool:
    low = (reply or "").lower().strip()
    bad = (
        "", "entendi.", "entendi. continua.",
        "próximo passo objetivo: definir entrada",
        "proximo passo objetivo: definir entrada",
        "vamos aprofundar sem reiniciar a conversa"
    )
    return (not low) or any(x in low for x in bad)

def _p412n_rescue_if_bad(sender_id: str, message: str, reply: str) -> str:
    if not _p412n_response_quality_bad(reply):
        return reply
    from app.runtime.universal_conversation_os import UniversalConversationOS
    rescued = UniversalConversationOS.process(message, sender_id, candidate_reply="").get("reply")
    return rescued or reply

def _p412n_normalize_xml_response(message: str, xml: str) -> str:
    import re
    raw = str(xml or "")
    m = re.search(r"<Message>(.*?)</Message>", raw, flags=re.S)
    body = m.group(1).strip() if m else raw.strip()
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(body))}</Message></Response>'


# P4_28U_FORCE_REAL_WEBHOOK_TO_API_RUNTIME
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    from fastapi.responses import Response
    from app.api.whatsapp import eldora_primary_runtime_reply, twiml
    form = await request.form()
    body = str(form.get("Body", "") or "")
    sender = str(form.get("From", "") or "whatsapp:unknown")
    reply = eldora_primary_runtime_reply(sender, body)
    return Response(content=twiml(reply), media_type="application/xml")


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
        content=f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{sanitize_final_human_output(sanitize_final_human_output(reply))}</Message></Response>',
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

from app.api.eldora_runtime_canonical import router as eldora_runtime_canonical_router
app.include_router(eldora_runtime_canonical_router)

from app.api.eldora_cognitive_runtime import router as eldora_cognitive_runtime_router
app.include_router(eldora_cognitive_runtime_router)

from app.api.whatsapp import router as whatsapp_router
app.include_router(whatsapp_router)

from app.api.eldora_autonomous_cognition import router as eldora_autonomous_cognition_router
app.include_router(eldora_autonomous_cognition_router)



from app.api.diagnostic_twilio import router as diagnostic_twilio_router
app.include_router(diagnostic_twilio_router)


from app.api.debug_whatsapp_state import router as debug_whatsapp_state_router
app.include_router(debug_whatsapp_state_router)

from app.api.debug_whatsapp_source import router as debug_whatsapp_source_router
app.include_router(debug_whatsapp_source_router)

from app.api.debug_whatsapp_runtime_trace import router as debug_whatsapp_runtime_trace_router
app.include_router(debug_whatsapp_runtime_trace_router)


# FINAL_IDENTITY_BLOCK
def __identity_guard_last_hop(answer,user_message=""):
    return enforce_no_identity_in_normal_chat(user_message,answer)



from app.api.eldora_telemetry import router as eldora_telemetry_router
app.include_router(eldora_telemetry_router)


from app.api.eldora_swarm import router as eldora_swarm_router
app.include_router(eldora_swarm_router)


from app.api.eldora_swarm_monitor import router as eldora_swarm_monitor_router
app.include_router(eldora_swarm_monitor_router)





# P4_12N_FORENSIC_TRACE_DUMP_ENDPOINT
@app.get("/__forensic/trace")
def __forensic_trace_dump():
    from pathlib import Path
    path = Path("_evidence/WHATSAPP_RUNTIME_TRACE/RUNTIME_PIPELINE_TRACE.jsonl")
    if not path.exists():
        return {"exists": False, "path": str(path), "lines": []}
    return {
        "exists": True,
        "path": str(path),
        "lines": path.read_text(encoding="utf-8", errors="ignore").splitlines()[-500:]
    }


# P4_12N_ROUTE_DUMP_ENDPOINT
@app.get("/__forensic/routes")
def __forensic_routes():
    return [{"path": getattr(r, "path", None), "name": getattr(r, "name", None), "methods": sorted(list(getattr(r, "methods", []) or [])), "endpoint": getattr(getattr(r, "endpoint", None), "__module__", None)+"."+getattr(getattr(r, "endpoint", None), "__name__", "")} for r in app.routes]





@app.get("/p4-13g-proof")
def p4_13g_proof():
    from app.runtime.p4_13g_router import route_natural_whatsapp
    return {
        "proof": "P4_13G_DEPLOY_PROOF",
        "expected_head": "d1e117764ef7383308f48288e18550ee34b9f341",
        "bmw": route_natural_whatsapp("quero comprar uma moto k1300 quais são as melhores qualidades dela?"),
        "holambra": route_natural_whatsapp("me diga um ponto turistico em Holambra")
    }




from app.api.canary_routes import router as canary_router
app.include_router(canary_router)


from app.api.p414_routes import router as p414_router
app.include_router(p414_router)



@app.get("/__p428s/trace")
def __p428s_trace():
    return {"events": _P428S_TRACE_BUFFER[-50:]}

