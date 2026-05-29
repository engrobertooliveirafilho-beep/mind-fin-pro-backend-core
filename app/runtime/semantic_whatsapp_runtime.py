from app.runtime.semantic_router import semantic_route
from app.runtime.real_factual_provider import real_factual_provider

_CONTEXT = {}

def _ctx_for_domain(global_ctx, domain):
    keep = {"last_location"} if domain in ("local_food", "travel") else set()
    return {k: v for k, v in global_ctx.items() if k in keep}

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    sid = sender_id or "default"
    global_ctx = _CONTEXT.get(sid, {})
    first = semantic_route(message, global_ctx)
    scoped_ctx = _ctx_for_domain(global_ctx, first.domain)

    decision = semantic_route(message, scoped_ctx)
    for k, v in (decision.entities or {}).items():
        if k == "location":
            global_ctx["last_location"] = v
    global_ctx["last_domain"] = decision.domain
    _CONTEXT[sid] = global_ctx

    provider = real_factual_provider(message, sid, scoped_ctx)
    answer = provider["answer"] if provider.get("ok") else provider["answer"]

    return {
        "intent": decision.intent,
        "domain": decision.domain,
        "confidence": decision.confidence,
        "entities": decision.entities,
        "context": global_ctx,
        "provider_ok": provider.get("ok", False),
        "provider": provider.get("provider"),
        "answer": answer[:900],
    }

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_whatsapp_payload(message, sender_id).get("answer", "")
