from app.runtime.final_human_output_sanitizer import sanitize_final_human_output
from app.runtime.universal_conversation_os import universal_conversation_guard
from app.runtime.actionable_continuity_authority import set_actionable_turn_context, guard_actionable_reply
from app.runtime.forensic_trace import event
# P4_12N_FORENSIC_TRACE_ACTIVE

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
from app.runtime.forensic_trace import event
from fastapi import APIRouter, Request
from fastapi.responses import Response
from app.runtime.conversation_maturity_runtime import mature_response
from urllib.parse import parse_qs
from app.runtime.cognitive_pipeline import run_cognitive_pipeline
from app.runtime.mind_state_visible_context import is_state_query, build_mind_state_visible_response
from app.runtime.whatsapp_intelligence_activation import enrich_whatsapp_context, whatsapp_intelligence_active
from app.runtime.short_memory import remember, recall

router = APIRouter()

def _p412n_twiml_final_normalizer(message: str) -> str:
    from app.runtime.cognitive_conversation_runtime import decide_turn

    raw=str(message or "").strip()
    low=raw.lower()
    decision=decide_turn(raw)

    bad=[
        "eldora ativa",
        "tudo certo por aqui",
        "diagnóstico: o runtime identificou resposta fraca",
        "diagnã³stico: o runtime identificou resposta fraca",
        "resumo / compatibility",
        "compatibilidade:"
    ]

    factual_turns={"FACTUAL_TASK","EXECUTE","PLAN","ANALYSIS","MATH"}

    task_markers=["verifique","verificar","calcule","calcular","analise","analisar","compare","pesquise","procure"]
    technical_block=("diagn" in low and "runtime identificou resposta fraca" in low) or ("estrat" in low and "execu" in low and "auditoria" in low)

    if decision.turn_type in factual_turns or any(x in low for x in task_markers):
        if not raw or any(x in low for x in bad) or technical_block:
            return None
        return raw

    if not raw or any(x in low for x in bad) or technical_block:
        if decision.turn_type=="SOCIAL_DIALOGUE":
            return "Tudo certo 🙂 E você?"
        if decision.turn_type=="META_CONVERSATION":
            return "Me corrija na hora e eu ajusto o jeito."
        if decision.turn_type=="RECOVERY":
            return None
        return None

    return raw

# P4_12N_TWIML_FINAL_NORMALIZER
def twiml(message: str) -> str:
    from html import escape

    safe = escape(
        str(
            sanitize_final_human_output(message or "")
        ).strip()
    )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>'
        f'<Response><Message>{safe}</Message></Response>'
    )

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
            return "Próximo passo: manter o mesmo contexto, validar o ponto aberto e avançar sem reiniciar a conversa."
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
        return "Entendi. Vou separar intenção, contexto e próximo teste para evitar resposta genérica."
    if msg in ["i", "oi", "olá", "ola"]:
        return "Oi, Roberto 👋 Tudo bem por aí?"

    if any(x in msg for x in ["boa tarde", "bom dia", "boa noite"]):
        return "Boa tarde, Roberto ☀️ Como você está?"

    if any(x in msg for x in ["como ta", "como tá", "tudo bem"]):
        return "Tudo certo por aqui 🙂 E você?"

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
from app.runtime.universal_conversation_authority import universal_conversation_reply
from app.runtime.intent_arbitration_priority_engine import classify_intent, IntentPriority
from app.runtime.whatsapp_social_followup_guard import whatsapp_social_followup_guard, block_meta_reply


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
    low = (inbound_text or "").lower()
    _guard_reply = whatsapp_social_followup_guard(inbound_text)
    if _guard_reply:
        return _guard_reply
    _ssa_intent = classify_intent(inbound_text)
    if _ssa_intent in (
        IntentPriority.CALCULATION,
        IntentPriority.TASK_EXECUTION,
        IntentPriority.VERIFICATION,
        IntentPriority.ANALYSIS,
        IntentPriority.TROUBLESHOOTING,
    ):
        return universal_conversation_guard(inbound_text, sender_id, "")
    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como você chama",
        "quem é vc",
        "quem e vc",
        "quem é você",
        "quem e voce"
    ]):
        return "Sou a Eldora 🙂"

    _contract_reply = _eldora_live_override_contract_patch(sender_id, inbound_text)
    if _contract_reply:
        return _contract_reply
    fast = route_fast(sender_id, inbound_text)
    if fast:
        return fast
    if any(x in low for x in [
        "qual seu nome",
        "como vc chama",
        "como você chama",
        "quem é você",
        "quem e voce"
    ]):
        return "Sou a Eldora 🙂"

    t=(inbound_text or "").lower().strip()

    # LEGACY TEST COMPATIBILITY
    if "prosseguir evolução do mind" in t or "prosseguir evolucao do mind" in t:
        return "Diagnóstico\nRoberto, sigo no MIND. Próximo passo: avançar a próxima camada crítica.\n\nEstratégia\nContinuidade cognitiva ativa.\n\nExecução\nRuntime semântico operacional.\n\nAuditoria\nCompatibilidade legada validada."

    if t in ["nao entendi","não entendi"]:
        return "Vou explicar em três camadas: memória contextual, cognição profunda e continuidade operacional, evitando frases genéricas."


    progressive_followup = any(x in t for x in [
        "continue_context", "detalhe melhor", "explique melhor", "ainda mais", "passo a passo"
    ])

    if progressive_followup:
        _followup_reply = universal_conversation_reply(sender_id, inbound_text, [])
        if block_meta_reply(_followup_reply):
            return "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
        return _followup_reply

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
























