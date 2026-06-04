import re

def humanized_answer(message: str, answer: str, ctx: dict | None = None) -> str:
    msg = str(message or "").lower()
    ctx = ctx or {}
    subject = ctx.get("last_subject", "")

    if ctx.get("last_domain") == "vehicle_buying" and subject:
        if any(x in msg for x in ["fraco", "defeito", "problema"]):
            return f"Olha, os pontos fracos da {subject} são idade, manutenção mal feita e peças cansadas. Eu olharia motor frio, elétrica, suspensão, freios e documento. Se tiver gambiarra ou histórico fraco, melhor fugir."

        if any(x in msg for x in ["vale a pena"]):
            return f"Vale a pena avaliar {subject}, mas só com evidências reais: histórico, inspeção, manutenção comprovada e custo futuro. Sem prova, eu negociaria forte ou deixaria passar."

        if any(x in msg for x in ["prossiga", "aprofunde", "continue"]):
            return f"Vamos direto: na {subject}, o segredo é não se apaixonar pela aparência. Primeiro veja motor frio, elétrica, suspensão e documento. Moto antiga boa existe, mas moto maquiada vira gasto rápido."

    out = str(answer or "").strip()
    out = re.sub(r"\s+", " ", out)
    out = out.replace("Aqui estão algumas dicas", "Olha")
    out = out.replace("pode ajudá-lo", "pode te ajudar")
    return out
