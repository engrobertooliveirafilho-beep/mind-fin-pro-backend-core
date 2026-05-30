import re

def detect_subject(message: str) -> str:
    t = (message or "").lower()
    patterns = [
        (r"\bcb\s*500\b|\bcb500\b|\bsobre a cb\b", "Honda CB500 ano 2000 usada"),
        (r"\bfazer\s*250\b", "Yamaha Fazer 250 usada"),
        (r"\bbmw\s*k\s*1300\b|\bk1300\b", "BMW K1300 usada"),
        (r"\bhornet\b", "Honda Hornet usada"),
        (r"\bxre\s*300\b", "Honda XRE 300 usada"),
        (r"\bmt\s*03\b|\bmt03\b", "Yamaha MT-03 usada"),
    ]
    for pat, sub in patterns:
        if re.search(pat, t):
            return sub
    m = re.search(r"comprar\s+(uma|um)?\s*(.+)", t)
    if m:
        return "veículo usado: " + m.group(2).strip(" ?.!")[:80]
    return ""

def detect_domain(message: str) -> str:
    t = (message or "").lower()
    if any(x in t for x in ["moto","cb500","cb 500","fazer","k1300","hornet","xre","mt03","comprar","manutenção","consumo","pontos fortes","pontos fracos"]):
        return "vehicle_buying"
    return "general"

def detect_followup_intent(message: str) -> str:
    t = (message or "").lower().strip()
    if t in {"prossiga","continue","continua","aprofunde","aprofundar","detalhe","mais detalhes"}:
        return "continue"
    if "fraco" in t or "defeito" in t or "problema" in t:
        return "weaknesses"
    if "forte" in t or "qualidade" in t:
        return "strengths"
    if "manutenção" in t or "manutencao" in t:
        return "maintenance"
    if "consumo" in t or "gasta" in t:
        return "consumption"
    if "vale a pena" in t:
        return "decision"
    if len(t.split()) <= 4:
        return "followup"
    return ""

def build_conversation_payload(message: str, ctx: dict) -> str:
    subject = detect_subject(message)
    domain = detect_domain(message)
    if subject:
        ctx["last_subject"] = subject
        ctx["last_domain"] = domain

    intent = detect_followup_intent(message)
    if intent and ctx.get("last_subject"):
        subject = ctx["last_subject"]
        domain = ctx.get("last_domain", "general")
        return f"""
Você é a Eldora, assistente próxima do Roberto no WhatsApp.
Responda em português do Brasil, como uma amiga inteligente, prática e direta.
NÃO responda como ChatGPT genérico.
NÃO mude de assunto.
NÃO explique o termo isolado.
Use obrigatoriamente o contexto abaixo.

DOMÍNIO: {domain}
ASSUNTO ATUAL: {subject}
INTENÇÃO DO USUÁRIO: {intent}
MENSAGEM ORIGINAL: {message}

Se domínio for vehicle_buying:
- fale como quem ajuda a comprar sem cair em furada;
- seja objetiva;
- máximo 4 blocos curtos;
- cite pontos práticos: estado, manutenção, custo, risco, decisão.
""".strip()

    return message
