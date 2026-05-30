import re

FOLLOWUP_PATTERNS = [
    "aprofunde","aprofundar","continue","continua","detalhe","mais detalhes",
    "explique mais","sobre isso","e os pontos fracos","pontos fracos",
    "e manutenção","manutenção","e consumo","consumo","vale a pena"
]

def extract_subject(message: str) -> str:
    msg = str(message or "").strip()
    low = msg.lower()

    m = re.search(r"\b(bmw\s*k\s*1300|bmw\s*k1300|k1300|fazer\s*250|xre\s*300|cb\s*500|crf\s*250|hornet|mt\s*03)\b", low, re.I)
    if m:
        return m.group(1).upper().replace("  ", " ")

    m = re.search(r"(comprar|vale a pena|pontos fortes|pontos fracos)\s+(uma|um|a|o)?\s*(.+)", low)
    if m:
        return m.group(3).strip(" ?.!")[:80]

    return ""

def is_followup(message: str) -> bool:
    low = str(message or "").strip().lower()
    return low in FOLLOWUP_PATTERNS or len(low.split()) <= 3 and any(x in low for x in ["isso","ela","ele","manutenção","consumo","fracos"])

def update_topic_context(message: str, ctx: dict, domain: str = "") -> dict:
    subject = extract_subject(message)
    if subject:
        ctx["last_subject"] = subject
    if domain:
        ctx["last_domain"] = domain
    return ctx

def expand_followup(message: str, ctx: dict) -> str:
    if is_followup(message) and ctx.get("last_subject"):
        return f"{message}. Contexto obrigatório: responder sobre {ctx['last_subject']}."
    return message
