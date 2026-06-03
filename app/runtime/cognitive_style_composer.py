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
        label = "esse veículo"
        raw = str(subject or "").lower()
        if any(x in raw for x in ["ram", "hilux", "ranger", "s10", "amarok", "frontier"]): label = "essa caminhonete"
        elif any(x in raw for x in ["corolla", "civic", "onix", "hb20", "carro"]): label = "esse carro"
        elif any(x in raw for x in ["crf", "cb", "xre", "hornet", "cbr", "r6", "moto"]): label = "essa moto"
        if any(x in msg for x in ["fraco","defeito","problema"]):
            return f"Olha, os pontos fracos de {label} são idade, manutenção mal feita e desgaste escondido. Eu olharia histórico, documentação, uso anterior e sinais de gambiarra."
        if "vale a pena" in msg:
            return f"Pode valer a pena, mas só se {label} estiver bem cuidado e fizer sentido no preço. Eu validaria histórico, custo de manutenção e estado real antes de fechar."
        if any(x in msg for x in ["prossiga","aprofunde","continue"]):
            return f"Sobre {label}, o segredo é não decidir só pela aparência. Valide histórico, uso anterior, manutenção, documentação e custo futuro antes de comprar."
        return f"Olha, {label} pode ser uma boa compra se estiver bem cuidado. {core} Antes de animar, eu validaria histórico, manutenção, documentação e custo futuro."

    return core or text
