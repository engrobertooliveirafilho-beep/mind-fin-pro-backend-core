import re

FOLLOWUP_WORDS={
    "prossiga","continue","continua","aprofunde","aprofundar","detalhe",
    "mais detalhes","explique","explica","como","como?","e depois","depois",
    "por que","porque","why","what","que foi","me explique","seja mais especifico",
    "seja mais específico"
}

STRONG_INTENTS=[
    "quero","preciso","comprar","montar","criar","fazer","analisar","analise",
    "verificar","verifique","explicar","explique","planejar","planeje","calcular",
    "calcule","organizar","resolver","corrigir","corrija","automatizar","comparar"
]

DOMAIN_RULES=[
    ("vehicle_buying",["comprar","veiculo","veículo","carro","moto","caminhonete","caminhao","caminhão","manutencao","manutenção","consumo","por litro","km/l"]),
    ("agro_business",["boi","bois","gado","confinamento","pecuaria","pecuária","fazenda","arroba","cocho","frigorifico","frigorífico"]),
    ("marketing",["marketing","anuncio","anúncio","campanha","criativo","copy","venda","lead","funil","trafego","tráfego"]),
    ("technology",["runtime","render","supabase","github","webhook","api","deploy","commit","pytest","drive"]),
]

def _norm(message: str) -> str:
    return re.sub(r"\s+"," ",str(message or "").lower().strip())

def is_followup(message:str)->bool:
    t=_norm(message)
    if not t:
        return False
    if t in FOLLOWUP_WORDS:
        return True
    if len(t.split()) <= 4 and not any(x in t for x in STRONG_INTENTS):
        return True
    return any(x in t for x in [
        "ela","ele","isso","esse","essa","sobre isso","quanto","por litro",
        "km/l","vale a pena","manutencao","manutenção","consumo","pontos fracos",
        "pontos fortes","detalhe","detalhar","explique","explica","continue",
        "continua","como fazer","como seria"
    ])

def detect_followup_intent(message: str) -> str:
    return "followup" if is_followup(message) else ""

def detect_subject(message: str) -> str:
    t=_norm(message)
    if not t:
        return ""
    cleaned=re.sub(r"[?!.]+$","",t).strip()
    strong_intent=any(x in cleaned for x in STRONG_INTENTS)
    if strong_intent and len(cleaned.split()) >= 3 and not is_followup(cleaned):
        return cleaned[:220]
    if len(cleaned.split()) >= 5 and not is_followup(cleaned):
        return cleaned[:220]
    return ""

def detect_domain(message: str) -> str:
    t=_norm(message)
    for domain, terms in DOMAIN_RULES:
        if any(x in t for x in terms):
            return domain
    return "general"

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
