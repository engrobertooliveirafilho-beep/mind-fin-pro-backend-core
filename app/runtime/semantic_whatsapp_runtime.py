from app.runtime.semantic_router import semantic_route
from app.runtime.multi_provider_factual_provider import multi_provider_factual_provider
from app.runtime.whatsapp_ux_output_guard import whatsapp_ux_guard

_CONTEXT = {}

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    sid = sender_id or "default"

    ctx = _CONTEXT.get(sid, {})

    decision = semantic_route(message, ctx)

    entities = getattr(decision, "entities", {}) or {}
    for k, v in entities.items():
        if v:
            ctx[k] = v

    ctx["last_domain"] = getattr(decision, "domain", "general")
    _CONTEXT[sid] = ctx

    provider = multi_provider_factual_provider(message, sid, ctx)

    answer = (
        provider["answer"]
        if provider.get("ok")
        else getattr(decision, "answer", "Recebi. Reformule em uma frase.")
    )

    answer = whatsapp_ux_guard(message, answer)

    return {
        "intent": getattr(decision, "intent", "UNKNOWN"),
        "domain": getattr(decision, "domain", "general"),
        "confidence": getattr(decision, "confidence", 0.0),
        "entities": entities,
        "context": ctx,
        "provider_ok": provider.get("ok", False),
        "provider": provider.get("provider"),
        "model": provider.get("model"),
        "answer": answer,
        "errors": provider.get("errors", []),
    }

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_whatsapp_payload(message, sender_id).get("answer", "")
