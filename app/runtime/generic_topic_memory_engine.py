import re

FOLLOWUP_PATTERNS = [
    "aprofunde","aprofundar","continue","continua","detalhe","mais detalhes",
    "explique mais","sobre isso","e os pontos fracos","pontos fracos",
    "e manutenção","manutenção","e consumo","consumo","vale a pena"
]

def extract_subject(message: str) -> str:
    low = str(message or "").strip().lower()

    if re.search(r"\bfazer\s*250\b", low):
        return "Yamaha Fazer 250 usada"
    if re.search(r"\b(bmw\s*k\s*1300|bmw\s*k1300|k1300)\b", low):
        return "BMW K1300 usada"

    m = re.search(r"(comprar|vale a pena|pontos fortes|pontos fracos)\s+(uma|um|a|o)?\s*(.+)", low)
    if m:
        subject = m.group(3).strip(" ?.!")[:80]
        if any(x in low for x in ["moto","carro","veículo","veiculo","usada","usado"]):
            return "compra de veículo usado: " + subject
        return subject

    return ""

def infer_domain(message: str) -> str:
    low = str(message or "").lower()
    if any(x in low for x in ["moto","carro","bmw","k1300","fazer 250","usada","usado","comprar","manutenção","consumo"]):
        return "vehicle_buying"
    return ""

def is_followup(message: str) -> bool:
    low = str(message or "").strip().lower()
    return low in FOLLOWUP_PATTERNS or (len(low.split()) <= 3 and any(x in low for x in ["isso","ela","ele","manutenção","consumo","fracos"]))

def update_topic_context(message: str, ctx: dict, domain: str = "") -> dict:
    subject = extract_subject(message)
    inferred = infer_domain(message)
    if subject:
        ctx["last_subject"] = subject
    if inferred:
        ctx["last_domain"] = inferred
    elif domain:
        ctx["last_domain"] = domain
    return ctx

def expand_followup(message: str, ctx: dict) -> str:
    if is_followup(message) and ctx.get("last_subject"):
        domain = ctx.get("last_domain", "general")
        if domain == "vehicle_buying":
            return f"{message}. Contexto obrigatório: continue sobre compra de veículo usado, assunto: {ctx['last_subject']}. Fale de pontos fortes, pontos fracos, manutenção, riscos e checklist."
        return f"{message}. Contexto obrigatório: responder sobre {ctx['last_subject']}."
    return message
