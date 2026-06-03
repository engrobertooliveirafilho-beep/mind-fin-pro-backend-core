import re

FOLLOWUP_WORDS={"prossiga","continue","continua","aprofunde","aprofundar","detalhe","mais detalhes","explique","como","como?","e depois","depois","por que","porque","why","what","que foi"}

def detect_subject(message: str) -> str:
    t=(message or "").lower().strip()
    if not t: return ""
    patterns=[
        (r"\bcb\s*500\b|\bcb500\b|\bsobre a cb\b","Honda CB500 ano 2000 usada"),
        (r"\bfazer\s*250\b","Yamaha Fazer 250 usada"),
        (r"\bbmw\s*k\s*1300\b|\bk1300\b","BMW K1300 usada"),
        (r"\bhornet\b","Honda Hornet usada"),
        (r"\bxre\s*300\b","Honda XRE 300 usada"),
        (r"\bmt\s*03\b|\bmt03\b","Yamaha MT-03 usada"),
    ]
    for pat,sub in patterns:
        if re.search(pat,t): return sub
    cleaned=re.sub(r"[?!.]+$","",t).strip()
    if len(cleaned.split())>=5 and not is_followup(cleaned) and not any(x in cleaned for x in ["explique","explica","etapas","detalhe","detalhar","como fazer","como seria"]):
        return cleaned[:140]
    return ""

def detect_domain(message: str) -> str:
    t=(message or "").lower()
    if any(x in t for x in ["moto","cb500","cb 500","fazer","k1300","hornet","xre","mt03","carro","comprar","manutenção","consumo"]): return "vehicle_buying"
    if any(x in t for x in ["boi","bois","gado","confinamento","pecuaria","pecuária","fazenda","arroba","cocho"]): return "agro_business"
    if any(x in t for x in ["marketing","anuncio","anúncio","campanha","criativo","copy","venda"]): return "marketing"
    return "general"

def is_followup(message:str)->bool:
    t=(message or "").lower().strip()
    return t in FOLLOWUP_WORDS or len(t.split())<=4 or any(x in t for x in ["explique","explica","etapas","detalhe","detalhar","como fazer","como seria"])

def detect_followup_intent(message: str) -> str:
    t=(message or "").lower().strip()
    if t in FOLLOWUP_WORDS: return "followup"
    if len(t.split())<=4: return "followup"
    return ""

def build_conversation_payload(message: str, ctx: dict) -> str:
    subject=detect_subject(message)
    domain=detect_domain(message)
    if subject:
        ctx["last_subject"]=subject
        ctx["last_domain"]=domain
        ctx["last_user_message"]=message

    intent=detect_followup_intent(message)
    if intent and (ctx.get("last_subject") or ctx.get("last_user_message")):
        subject=ctx.get("last_subject") or ctx.get("last_user_message")
        domain=ctx.get("last_domain","general")
        return f"""Você é a Eldora no WhatsApp.
Responda SEMPRE em português do Brasil.
Continue obrigatoriamente o assunto anterior.
Não traduza a mensagem.
Não responda em inglês, francês ou espanhol.
Não explique a palavra isolada.

DOMÍNIO: {domain}
ASSUNTO ATUAL: {subject}
INTENÇÃO: {intent}
NOVA MENSAGEM: {message}

Responda como continuação prática do assunto atual, com no máximo 5 blocos curtos."""
    return message
