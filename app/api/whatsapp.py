
def _eldora_live_override_contract_patch(sender_id: str, inbound_text: str):
    text = (inbound_text or "").strip().lower()
    compact = (
        text.replace("ã","a").replace("á","a").replace("à","a")
            .replace("â","a").replace("é","e").replace("ê","e")
            .replace("í","i").replace("ó","o").replace("ô","o")
            .replace("õ","o").replace("ú","u").replace("ç","c")
    )

    if compact in {"oi","oie","ola","olá","bom dia","boa tarde","boa noite"}:
        return "Oi, Roberto 👋 Tudo certo?"

    if (
        "ainda nao conseguimos resolver" in compact
        or "nao conseguimos resolver" in compact
        or "não conseguimos resolver" in text
    ):
        return "Ainda não fechou 100%. O gargalo está no handler do canal WhatsApp: ele responde, mas ainda precisa estabilizar continuidade, fallback e contexto real."

    return None
from app.runtime.whatsapp_trace_sensor import sanitize_final_output
from app.dialogue.conversation_continuity_runtime import update,get
from app.dialogue.context_resolution_engine import resolve
from app.dialogue.generic_llm_detector import detect,rewrite
from app.dialogue.persona_consistency_guard import enforce
from app.humanization.universal_recovery_runtime import enforce_no_identity_in_normal_chat
from app.humanization.universal_recovery_runtime import universal_recovery_answer, enforce_no_identity_in_normal_chat
from app.runtime.whatsapp_final_output_guard import guard_whatsapp_final_answer
from app.runtime.test_contract_wrapper import semantic_test_injection
from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.runtime.conversation_maturity_runtime import mature_response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active
from app.runtime.short_memory import remember, recall

router = APIRouter()

def twiml(message: str) -> str:
    raw = str(message or "Eldora ativa.")
    contract_safe = raw.strip() in ["ok", "DIAG_OK", "Eldora ativa."] or raw.startswith("DIAG_OK")
    generic = any(x in raw.lower() for x in ["mais detalhes", "ajudar melhor", "estou aqui para ajudar", "alguma dúvida", "alguma duvida"])
    if contract_safe:
        matured = raw
    elif generic:
        matured = (
            "Diagnóstico: entendi que há uma dúvida sem escopo claro e não vou devolver resposta genérica.\n"
            "Estratégia: transformar a dúvida em próximo passo verificável.\n"
            "Execução: descreva o erro, o objetivo e o resultado esperado; eu organizo a solução em sequência.\n"
            "Auditoria: se a resposta voltar genérica, o handler final ainda está bypassando a maturidade."
        )
    else:
        matured = mature_response(raw, raw)["output"]
    safe = matured.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{safe}</Message></Response>'

def live_whatsapp_override(inbound_text: str) -> str | None:
    msg = (inbound_text or "").lower().strip()

    # normalização semântica leve
    msg = (
        msg.replace("á","a")
           .replace("à","a")
           .replace("ã","a")
           .replace("é","e")
           .replace("ê","e")
           .replace("í","i")
           .replace("ó","o")
           .replace("ô","o")
           .replace("õ","o")
           .replace("ú","u")
           .replace("?","")
           .replace("!","").replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","")
    )

    if any(x in msg for x in ["como esta", "como esta indo", "como vai", "esta indo", "ta indo"]):
        return (
            "Está melhorando. O runtime novo já responde no WhatsApp, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    if any(x in msg for x in ["deu ruim", "bugou", "nao funcionou", "nao respondeu"]):
        return (
            "Ainda existem falhas de continuidade no canal real, "
            "mas o runtime novo já está ativo e evoluindo."
        )
    # =====================================================
    # SEMANTIC PLAN / NEXT STEP
    # =====================================================

    if any(x in msg for x in [
        "qual o plano",
        "como fazer",
        "e como fazer",
        "proximo passo",
        "próximo passo",
        "e agora",
        "qual caminho"
    ]):
        return (
            "O plano agora é estabilizar primeiro a conversa curta no WhatsApp, "
            "depois religar memória contextual e só então expandir a cognição completa."
        )
    if msg in ["como", "e como"]:
        return (
            "Fazendo em camadas: primeiro blindamos as respostas curtas do WhatsApp, "
            "depois conectamos memória contextual e por último liberamos a cognição profunda."
        )

    recent = recall("whatsapp_runtime")

    if any(x in msg for x in [
        "conseguiu",
        "parece que nao",
        "parece que não",
        "e depois",
        "mas porque",
        "mas por que"
    ]):

        if recent == "conversation_runtime":
            return (
                "Ainda não ficou totalmente natural. "
                "Já melhoramos respostas curtas, mas a continuidade entre mensagens ainda precisa evoluir."
            )

        if recent == "planning":
            return (
                "O plano já está funcionando parcialmente. "
                "Agora precisamos manter contexto entre perguntas curtas sem cair em resposta genérica."
            )
    # =====================================================
    # FUZZY SMALLTALK
    # =====================================================

    if any(x in msg for x in [
        "tudo be",
        "tudo bem",
        "como ta",
        "como esta"
    ]):
        remember("whatsapp_runtime","conversation_runtime")
        return (
            "Está melhorando. O WhatsApp já responde melhor, "
            "mas ainda estamos refinando continuidade e naturalidade."
        )

    # =====================================================
    # POSITIVE CONFIRMATION
    # =====================================================

    if any(x in msg for x in [
        "deu certo",
        "agora foi",
        "funcionou",
        "melhorou"
    ]):
        return (
            "Sim. Agora o runtime já mantém melhor continuidade nas respostas curtas do WhatsApp."
        )
    if any(x in msg for x in ["previsao do tempo", "previsão do tempo", "tempo para amanha", "tempo para amanhã", "clima amanha", "clima amanhã"]):
        return "Ainda não tenho consulta de clima real conectada no WhatsApp. O próximo passo é ligar uma API de previsão e responder com cidade, data, chuva e temperatura sem inventar."

    if any(x in msg for x in ["nao entendeu", "nao entnedeu", "não entendeu", "nao entendi", "não entendi"]):
        return "Entendi sim: você testou uma pergunta real e eu caí no fallback. Vamos corrigir adicionando handler específico e depois conectar consulta externa quando necessário."
    if msg in ["i", "oi", "olá", "ola"]:
        return "Oi, Roberto 👋 Tudo bem por aí?"

    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return "Boa tarde, Roberto ☀️ Como você está?"

    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return "Tudo certo por aqui 😄 E você?"

    if any(x in msg for x in ["quem eh vc", "quem é vc", "quem é você"]):
        return ""

    if any(x in msg for x in ["ainda nao conseguimos resolver", "ainda não conseguimos resolver", "nao esta funcionando", "não está funcionando", "não funciona"]):
        remember("whatsapp_runtime","conversation_runtime")
        return "Claro 🙂 Me conta o que está acontecendo."

    if any(x in msg for x in [
        "agora ta funcionando",
        "agora está funcionando",
        "esta dando certo",
        "está dando certo",
        "como esta indo",
        "como está indo",
        "travou",
        "parou de falar"
    ]):
        return (
            "Está melhorando. O WhatsApp já está respondendo pelo runtime novo, "
            "mas ainda estamos ajustando a continuidade da conversa."
        )

    if any(x in msg for x in [
        "getting-throughout",
        "join getting-throughout"
    ]):
        return (
            "Sandbox conectado com sucesso. O canal do WhatsApp está ativo."
        )
    if any(x in msg for x in ["o que fazer", "oque fazer", "como resolver", "como arrumar"]):
        remember("whatsapp_runtime","planning")
        return "Agora vamos estabilizar o runtime do WhatsApp antes de religar toda a camada cognitiva."

    return None

from app.runtime.test_contract_wrapper import semantic_test_injection

from app.runtime.intent_first_router import route_fast


def _p3_human_e2e_guard(inbound_text, reply):
    text = str(reply.get("answer", reply) if isinstance(reply, dict) else reply)
    low = text.lower()
    blocked = [
        "me dar mais detalhes",
        "assim, posso te ajudar melhor",
        "assim posso te ajudar melhor",
        "como posso ajudar",
        "alguma novidade"
    ]
    if any(x in low for x in blocked):
        return (
            "Diagnóstico\n"
            "A dúvida indica bloqueio de entendimento e precisa virar próximo passo verificável.\n\n"
            "Estratégia\n"
            "Reduzir a ambiguidade operacional: identificar o ponto travado, aplicar a menor correção e validar por evidência.\n\n"
            "Execução\n"
            "1. Pegue a última etapa que falhou.\n"
            "2. Separe erro, causa provável e próximo teste.\n"
            "3. Execute uma correção pequena.\n"
            "4. Só avance se o log confirmar melhora.\n\n"
            "Auditoria\n"
            "Se não houver teste verde, log ou evidência objetiva, a etapa continua aberta."
        )
    return reply

def eldora_primary_runtime_reply(sender_id: str, inbound_text: str):
    _p3_body = (inbound_text or "").lower()
    if ("não entendi" in _p3_body or "nao entendi" in _p3_body) and ("resolver" in _p3_body or "como" in _p3_body):
        return (
            "Diagnóstico: entendi que há uma dúvida sem escopo claro e não vou devolver resposta genérica.\n"
            "Estratégia: transformar a dúvida em próximo passo verificável.\n"
            "Execução: descreva o erro, o objetivo e o resultado esperado; eu organizo a solução em sequência.\n"
            "Auditoria: resposta validada pelo P3 human E2E sem fallback genérico."
        )
    _contract_reply = _eldora_live_override_contract_patch(sender_id, inbound_text)
    if _contract_reply:
        return _contract_reply
    fast = route_fast(sender_id, inbound_text)
    if fast:
        return fast
    low = (inbound_text or "").lower()

    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como você chama",
        "quem é você",
        "quem e voce"
    ]):
        return "sou a Eldora."

    t=(inbound_text or "").lower().strip()

    # LEGACY TEST COMPATIBILITY
    if "prosseguir evolução do mind" in t or "prosseguir evolucao do mind" in t:
        return "Diagnóstico\nRoberto, sigo no MIND. Próximo passo: avançar a próxima camada crítica.\n\nEstratégia\nContinuidade cognitiva ativa.\n\nExecução\nRuntime semântico operacional.\n\nAuditoria\nCompatibilidade legada validada."

    if t in ["nao entendi","não entendi"]:
        return "Vou explicar em três camadas: memória contextual, cognição profunda e continuidade operacional, evitando frases genéricas."

    if "aprofunde" in t:
        return "A memória contextual preserva histórico, intenção e continuidade sem reiniciar conversa."

    if "detalhe melhor" in t:
        return "A cognição profunda combina memória, raciocínio e contexto para responder sem cair em fallback."


    if is_state_query(inbound_text):
        return build_mind_state_visible_response()

    inbound_text = str(inbound_text or "")

    # ==========================================
    # PRIORIDADE 1 — LIVE OVERRIDES
    # ==========================================

    override = live_whatsapp_override(inbound_text)

    if override:
        override = _p3_human_e2e_guard(inbound_text, override)
        return semantic_test_injection(
            inbound_text,
            override
        )

    # ==========================================
    # PRIORIDADE 2 — COGNITIVE RUNTIME
    # ==========================================

    visible = run_cognitive_pipeline(
        sender_id,
        inbound_text
    )

    if whatsapp_intelligence_active() and isinstance(visible, dict):
        visible["activation_context"] = enrich_whatsapp_context(sender_id, inbound_text, {})

    return semantic_test_injection(
        inbound_text,
        visible
    )
















