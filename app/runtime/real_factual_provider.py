import json, os, re, urllib.request
from app.runtime.semantic_router import semantic_route, norm

OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def _call_llm(system, user):
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return None
    body = json.dumps({
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    }).encode("utf-8")
    req = urllib.request.Request(
        OPENAI_URL,
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()

def real_factual_provider(message: str, sender_id: str = "default", context: dict | None = None) -> dict:
    ctx = context or {}
    decision = semantic_route(message, ctx)

    system = (
        "Você é um assistente factual para WhatsApp. Responda em português do Brasil, curto, útil e direto. "
        "Não invente fonte, ranking ou dado atual se não tiver certeza. "
        "Para recomendações locais, dê critérios e opções prováveis apenas se forem conhecimento comum; se exigir atualização, diga que precisa de busca real. "
        "Para compra de veículo/produto, dê qualidades, riscos, checklist e próximo passo."
    )

    payload = {
        "message": message,
        "intent": decision.intent,
        "domain": decision.domain,
        "entities": decision.entities,
        "safe_context": ctx,
        "instruction": "gere a melhor resposta final para WhatsApp, sem metacomentário",
    }

    answer = _call_llm(system, json.dumps(payload, ensure_ascii=False))
    if answer:
        return {"ok": True, "provider": "openai", "answer": answer[:900]}

    return {
        "ok": False,
        "provider": "none",
        "answer": "Provider factual real não configurado. Configure OPENAI_API_KEY no Render para eu responder dinamicamente sem inventar."
    }
