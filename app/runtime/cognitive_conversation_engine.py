FOLLOWUP_WORDS = {
    "prossiga","continue","continua","aprofunde","aprofundar",
    "vale a pena","e manutenção","e os pontos fracos",
    "pontos fracos","consumo","e consumo","isso","sobre ela",
    "sobre a cb","sobre a moto","mais detalhes"
}

def cognitive_expand(message:str, ctx:dict):
    msg=(message or "").strip().lower()
    subject=ctx.get("last_subject","")
    domain=ctx.get("last_domain","general")

    if not subject:
        return message

    if msg in FOLLOWUP_WORDS:
        if domain=="vehicle_buying":
            return f"""
Continue uma conversa natural sobre compra da moto {subject}.

Fale curto, humano, útil e cognitivo.
Evite listas enormes.
Evite tom de ChatGPT.
Responda como uma amiga inteligente e prática.

Se for:
- pontos fracos → fale defeitos reais
- manutenção → custo, risco e dor de cabeça
- vale a pena → opinião contextual
- prossiga/aprofunde → continue o raciocínio anterior

Tema obrigatório: {subject}
Pergunta do usuário: {message}
""".strip()

    return message
