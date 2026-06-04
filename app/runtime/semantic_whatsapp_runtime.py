from app.runtime.semantic_router import semantic_route
from app.runtime.multi_provider_factual_provider import multi_provider_factual_provider
from app.runtime.whatsapp_ux_output_guard import whatsapp_ux_guard
from app.runtime.context_priority_engine import context_priority_reply
from app.runtime.humanized_answer_composer import humanized_answer
from app.runtime.cognitive_style_composer import compose_human_style
from app.runtime.relational_conversation_engine import relationalize
from app.runtime.conversation_state_machine import build_conversation_payload

_CONTEXT = {}

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    sid = sender_id or "default"
    ctx = _CONTEXT.get(sid, {})

    priority = context_priority_reply(message, sid)
    if priority:
        answer = whatsapp_ux_guard(message, priority)
        return {"intent":"CONTEXT_PRIORITY","domain":"project_context","confidence":0.99,"entities":{},"context":ctx,"provider_ok":False,"provider":"context_priority_engine","model":None,"answer":answer,"errors":[]}

    provider_message = build_conversation_payload(message, ctx)
    decision = semantic_route(provider_message, ctx)

    new_domain = getattr(decision, "domain", None)
    if new_domain and new_domain not in {"social","general"}:
        ctx["last_domain"] = new_domain
    elif not ctx.get("last_domain"):
        ctx["last_domain"] = new_domain or "general"
    _CONTEXT[sid] = ctx

    provider = multi_provider_factual_provider(provider_message, sid, ctx)
    answer = provider["answer"] if provider.get("ok") else getattr(decision, "answer", "Recebi. Reformule em uma frase.")
    if str(answer or "").strip().lower() in {"claro!","claro","certo!","certo","entendi!","entendi","ok","ok!"} and ctx.get("last_subject"):
        retry_msg = f"Explique de forma prática e completa sobre: {ctx.get('last_subject')}. Continue o contexto anterior. Responda em PT-BR com etapas concretas."
        retry = multi_provider_factual_provider(retry_msg, sid, ctx)
        if retry.get("ok") and len(str(retry.get("answer","")).strip()) > 40:
            answer = retry["answer"]
    answer = humanized_answer(message, answer, ctx)
    answer = compose_human_style(message, answer, ctx)
    answer = relationalize(message, answer, ctx)
    answer = whatsapp_ux_guard(message, answer)

    if str(answer or "").startswith("Não vou chutar número") and ctx.get("last_subject"):
        repair_msg = (
            f"Responda sobre {ctx.get('last_subject')} sem inventar números, preço, km ou datas. "
            f"Se não houver dado confiável, entregue checklist qualitativo prático com riscos, itens para verificar e decisão segura. "
            f"Pergunta original: {message}"
        )
        repair = multi_provider_factual_provider(repair_msg, sid, ctx)
        if repair.get("ok"):
            repaired = whatsapp_ux_guard(message, repair.get("answer",""))
            if not str(repaired or "").startswith("Não vou chutar número") and len(str(repaired).strip()) > 40:
                answer = repaired
    if str(answer or "").strip().lower() in {"claro!","claro","certo!","certo","entendi!","entendi","ok","ok!"} and ctx.get("last_subject"):
        retry_msg = f"Explique de forma prática e completa sobre: {ctx.get('last_subject')}. Continue o contexto anterior. Responda em PT-BR com etapas concretas."
        retry = multi_provider_factual_provider(retry_msg, sid, ctx)
        if retry.get("ok") and len(str(retry.get("answer","")).strip()) > 40:
            answer = whatsapp_ux_guard(message, retry["answer"])

    return {"intent":getattr(decision,"intent","UNKNOWN"),"domain":ctx.get("last_domain","general"),"confidence":getattr(decision,"confidence",0.0),"entities":{},"context":ctx,"provider_ok":provider.get("ok",False),"provider":provider.get("provider"),"model":provider.get("model"),"answer":answer,"errors":provider.get("errors",[])}

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_whatsapp_payload(message, sender_id).get("answer", "")



