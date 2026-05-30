import re

def compose_human_style(message:str, answer:str, ctx:dict|None=None)->str:
    ctx = ctx or {}
    subject = ctx.get("last_subject","")
    domain = ctx.get("last_domain","general")
    msg = str(message or "").lower()
    text = str(answer or "").strip()

    text = re.sub(r'Se você está pensando[^.]*\.', '', text, flags=re.I)
    text = re.sub(r'aqui estão[^.]*\.', '', text, flags=re.I)
    text = re.sub(r'que podem ajud[aá]-lo[^:;.]*[:.]?', '', text, flags=re.I)
    text = re.sub(r'que podem te ajudar[^:;.]*[:.]?', '', text, flags=re.I)
    text = re.sub(r'\b\d+\.\s*', '', text)

    text = re.sub(r'^\s*Olha,\s*sobre\s*a?\s*[^:]+:\s*', '', text, flags=re.I)
    text = re.sub(r'^\s*[A-Za-zÁ-Úá-ú0-9\s()./-]+:\s*', '', text)
    text = re.sub(r'\b[A-Za-z]{1,4}\s*\d{2,4}\s*\(\d{4}\):\s*', '', text, flags=re.I)

    text = re.sub(r'\bPrós:\s*', '', text, flags=re.I)
    text = re.sub(r'\bCuidados:\s*', '', text, flags=re.I)
    text = re.sub(r'\bPreço médio.*$', '', text, flags=re.I)
    text = re.sub(r'[⚠️✅💰🔧]', '', text)
    text = re.sub(r'\s+-\s+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    core = " ".join(sentences[:1]).strip()

    if domain == "vehicle_buying" and subject:
        if any(x in msg for x in ["fraco","defeito","problema"]):
            return "Olha, os pontos fracos dessa moto são idade, manutenção mal feita e peça cansada. Se fosse eu, olharia motor frio, elétrica, suspensão, freios e documento. Se tiver gambiarra ou histórico fraco, eu passaria."
        if "vale a pena" in msg:
            return "Eu teria coragem, mas só se essa moto estiver inteira. Eu compraria com laudo, teste frio e histórico de revisão. Se o dono não prova manutenção, negocia forte ou deixa passar."
        if any(x in msg for x in ["prossiga","aprofunde","continue"]):
            return "Nessa moto, o segredo é não se apaixonar pela aparência. Olha motor frio, elétrica, suspensão e documento. Moto antiga boa existe, mas às vezes parece boa no começo e depois começa a aparecer coisa escondida."
        return f"Olha, essa moto pode ser uma boa compra se estiver inteira. {core} Antes de animar, se fosse eu, olharia manutenção, elétrica, suspensão e documento."

    return core or text
