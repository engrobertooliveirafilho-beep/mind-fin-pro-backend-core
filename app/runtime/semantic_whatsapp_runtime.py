from app.runtime.semantic_router import semantic_route
from app.runtime.multi_provider_factual_provider import multi_provider_factual_provider

_CONTEXT = {}

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    sid = sender_id or "default"
    ctx = _CONTEXT.get(sid, {})
    decision = semantic_route(message, ctx)
    for k, v in (decision.entities or {}).items():
        if v: ctx[k]=v
    ctx["last_domain"]=decision.domain
    _CONTEXT[sid]=ctx

    provider = multi_provider_factual_provider(message, sid, ctx)
    answer = provider["answer"] if provider.get("ok") else decision.answer

    return {"intent":decision.intent,"domain":decision.domain,"confidence":decision.confidence,"entities":decision.entities,"context":ctx,"provider_ok":provider.get("ok",False),"provider":provider.get("provider"),"model":provider.get("model"),"answer":answer[:900],"errors":provider.get("errors",[])}

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_whatsapp_payload(message, sender_id).get("answer", "")
