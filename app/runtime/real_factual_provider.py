from app.runtime.semantic_router import semantic_route, norm

def real_factual_provider(message: str, sender_id: str = "default", context: dict | None = None) -> dict:
    ctx = context or {}
    d = semantic_route(message, ctx)
    loc = (d.entities or {}).get("location") or ctx.get("location")
    brand = (d.entities or {}).get("brand")
    model = (d.entities or {}).get("vehicle_model")
    subject = " ".join(x for x in [brand, model] if x) or loc or "o tema"

    if d.domain == "local_food":
        if not loc:
            return {"ok": False, "answer": "Me diga a cidade para eu recomendar restaurantes com critério."}
        return {"ok": True, "answer": f"Para restaurantes em {loc}, eu avaliaria: nota recente, volume de avaliações, tipo de cozinha, preço, localização e horário. A melhor resposta exige busca atualizada; posso listar por custo-benefício, romântico, família ou comida típica."}

    if d.domain == "vehicle_buying":
        return {"ok": True, "answer": f"Sobre {subject}: avalie motor, câmbio, suspensão, elétrica, histórico, disponibilidade de peças e custo de seguro. Boa compra só com laudo, teste frio e revisão documental."}

    if d.domain == "travel":
        return {"ok": True, "answer": f"Para viagem de fim de semana{(' em '+loc) if loc else ''}: escolha 1 atração principal, 1 restaurante, tempo real de estrada, estacionamento e plano B para chuva."}

    if d.domain == "math":
        return {"ok": True, "answer": d.answer}

    if d.domain == "social":
        return {"ok": True, "answer": d.answer}

    return {"ok": False, "answer": ""}
