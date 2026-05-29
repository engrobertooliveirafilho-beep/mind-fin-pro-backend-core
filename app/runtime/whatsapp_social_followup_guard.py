from __future__ import annotations
from app.runtime.intent_arbitration_priority_engine import classify_intent, IntentPriority

_BAD_META = ("runtime","branch","último retorno real","ultimo retorno real","execução contextual","execucao contextual","não recebi conteúdo","nao recebi conteudo","entendi. continua")

def whatsapp_social_followup_guard(message: str, last_context: str = "") -> str | None:
    msg=(message or "").strip()
    low=msg.lower()
    intent=classify_intent(msg)

    if ("como" in low and ("vc" in low or "você" in low or "voce" in low)) or intent == IntentPriority.SOCIAL:
        if "quem" in low:
            return "Sou a Eldora 🙂"
        if "como" in low and ("vc" in low or "você" in low or "voce" in low):
            return "Estou bem por aqui. E você?"
        return "Oi, Roberto 👋 Tudo certo?"

    if intent in (IntentPriority.FOLLOWUP_CONTEXTUAL, IntentPriority.OPEN_LOOP_CONTINUATION):
        ctx=(last_context or "").strip()
        if not ctx or ctx.lower() in {"isso","contexto anterior","o último ponto ainda aberto","ultimo ponto ainda aberto"}:
            return "Continua no mesmo ponto: validar o que falhou, testar a hipótese principal e avançar com evidência."
        return f"Continuando: {ctx}. Próximo passo: aprofundar a causa e validar por evidência."

    return None

def block_meta_reply(reply: str) -> bool:
    return any(x in (reply or "").lower() for x in _BAD_META)
