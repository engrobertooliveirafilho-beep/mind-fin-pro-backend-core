import re

def compose_human_style(message:str, answer:str, ctx:dict|None=None)->str:
    ctx = ctx or {}
    subject = ctx.get("last_subject","")
    domain = ctx.get("last_domain","general")
    msg = str(message or "").lower()
    text = str(answer or "").strip()

    text = re.sub(r'^\s*Olha,\s*sobre\s*a?\s*[^:]+:\s*', '', text, flags=re.I)
    text = re.sub(r'^\s*[A-Za-zÁ-Úá-ú0-9\s()./-]+:\s*', '', text)
    text = re.sub(r'\bPrós:\s*', '', text, flags=re.I)
    text = re.sub(r'\bCuidados:\s*', '', text, flags=re.I)
    text = re.sub(r'\bPreço médio.*$', '', text, flags=re.I)
    text = re.sub(r'[⚠️✅💰🔧]', '', text)
    text = text.replace("Aqui estão algumas dicas que podem te ajudar", "")
    text = text.replace("Aqui estão algumas dicas", "")
    text = text.replace("Olha, Olha,", "Olha,")
    text = re.sub(r'\s+', ' ', text).strip()

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    core = " ".join(sentences[:2]).strip()

    if domain == "vehicle_buying" and subject:
        if any(x in msg for x in ["fraco", "defeito", "problema"]):
            return f"Olha, os pontos fracos da {subject} são idade, manutenção mal feita e peça cansada. Eu olharia motor frio, elétrica, suspensão, freios e documento. Se tiver gambiarra ou histórico fraco, melhor fugir."

        if "vale a pena" in msg:
            return f"Vale a pena sim, mas só se a {subject} estiver inteira. Eu compraria com laudo, teste frio e histórico de revisão. Se o dono não prova manutenção, negocia forte ou deixa passar."

        if any(x in msg for x in ["prossiga","aprofunde","continue"]):
            return f"Na {subject}, o segredo é não se apaixonar pela aparência. Olha motor frio, elétrica, suspensão e documento. Moto antiga boa existe, mas moto maquiada vira gasto rápido."

        return f"Olha, a {subject} pode ser uma boa compra se estiver inteira. {core} Antes de animar, eu olharia manutenção, elétrica, suspensão e documento."

    return core or text
