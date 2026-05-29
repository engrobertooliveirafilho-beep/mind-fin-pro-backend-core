from app.runtime.semantic_router import semantic_route
from app.runtime.real_factual_provider import real_factual_provider

_CONTEXT = {}

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    sid = sender_id or "default"
    ctx = _CONTEXT.get(sid, {})
    decision = semantic_route(message, ctx)

    for k, v in (decision.entities or {}).items():
        if v:
            ctx[k] = v
    if decision.domain:
        ctx["domain"] = decision.domain
    _CONTEXT[sid] = ctx

    provider = real_factual_provider(message, sid, ctx)
    answer = provider["answer"] if provider.get("ok") else decision.answer

    return {
        "intent": decision.intent,
        "domain": decision.domain,
        "confidence": decision.confidence,
        "entities": decision.entities,
        "context": ctx,
        "provider_ok": provider.get("ok", False),
        "answer": answer[:900],
    }

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_whatsapp_payload(message, sender_id).get("answer", "")
