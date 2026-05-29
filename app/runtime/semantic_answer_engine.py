import re
from dataclasses import asdict
from app.runtime.semantic_router import semantic_route, norm

_CONTEXT = {}

LOCAL_FOOD_KB = {
    "holambra": [
        ("Casa Bela Café", "café/colonial", "boa opção para café, doces e experiência turística"),
        ("Martin Holandesa", "holandesa", "boa para comida típica e passeio"),
        ("The Old Dutch", "holandesa/europeia", "clássico para pratos típicos"),
        ("Zoet en Zout", "café/confeitaria", "bom para sobremesa, café e lanche"),
        ("Madurodam", "restaurante turístico", "boa escolha para almoço em roteiro de fim de semana"),
    ]
}

def _remember(sender_id, decision):
    sid = sender_id or "default"
    ctx = _CONTEXT.get(sid, {})
    ent = decision.entities or {}
    if ent.get("location"):
        ctx["location"] = norm(ent["location"])
    if decision.domain:
        ctx["domain"] = decision.domain
    _CONTEXT[sid] = ctx
    return ctx

def _answer_local_food(message, decision, ctx):
    loc = norm((decision.entities or {}).get("location") or ctx.get("location") or "")
    if not loc:
        return "Me diga a cidade para eu listar boas opções de restaurante."
    items = LOCAL_FOOD_KB.get(loc)
    if not items:
        return f"Para restaurantes em {loc}, eu preciso buscar opções atualizadas. Me diga faixa de preço ou tipo de comida."
    top = items[:5]
    linhas = [f"{i+1}. {nome} — {tipo}: {motivo}." for i, (nome, tipo, motivo) in enumerate(top)]
    return "Top 5 em Holambra:\n" + "\n".join(linhas)

def _answer_vehicle(message, decision):
    ent = decision.entities or {}
    model = " ".join(x for x in [ent.get("brand"), ent.get("vehicle_model")] if x) or "esse veículo"
    return (
        f"{model}: pontos fortes são motor forte, estabilidade, conforto e presença premium. "
        "Riscos: manutenção cara, elétrica, suspensão, peças e histórico. Antes de comprar, faça laudo e teste frio."
    )

def _answer_travel(message, decision, ctx):
    loc = norm((decision.entities or {}).get("location") or ctx.get("location") or "")
    if loc == "holambra":
        return "Em Holambra, monte o roteiro com Moinho Povos Unidos, centro turístico, almoço típico e parada para café/confeitaria."
    if loc:
        return f"Para {loc}, escolha 1 ponto principal, 1 restaurante, tempo de deslocamento e plano B se chover."
    return "Boa. Para viagem de fim de semana, defina cidade, tempo de estrada, hospedagem e 1 atração principal."

def semantic_answer(message, sender_id="default"):
    base_ctx = _CONTEXT.get(sender_id or "default", {})
    decision = semantic_route(message, base_ctx)
    ctx = _remember(sender_id, decision)

    if decision.domain == "local_food":
        answer = _answer_local_food(message, decision, ctx)
    elif decision.domain == "vehicle_buying":
        answer = _answer_vehicle(message, decision)
    elif decision.domain == "travel":
        answer = _answer_travel(message, decision, ctx)
    elif decision.domain == "math":
        answer = decision.answer
    elif decision.domain == "social":
        answer = decision.answer
    elif decision.intent == "FOLLOWUP":
        answer = decision.answer
    else:
        answer = decision.answer

    return {
        "intent": decision.intent,
        "domain": decision.domain,
        "confidence": decision.confidence,
        "entities": decision.entities,
        "context": ctx,
        "answer": answer[:900],
    }
