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
        if core:
            if len(core) >= 80:
                return core
            return f"{core} Valide evidências, riscos e custos antes de decidir."
        return f"Sobre {subject}, valide evidências, riscos e custos antes de decidir."

    return core or text

