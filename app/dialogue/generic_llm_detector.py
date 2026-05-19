BANNED=[
"como posso ajudar",
"alguma dúvida específica",
"alguma duvida especifica",
"me dê mais contexto",
"me de mais contexto",
"o score pode significar várias coisas",
"o score pode significar varias coisas",
"pode me explicar melhor",
"o que exatamente você quis dizer"
]
def detect(txt):
    low=(txt or "").lower()
    return any(x in low for x in BANNED)
def rewrite(txt,topic=""):
    low=(txt or "").lower()
    if "score" in low:
        return f"pelas {topic or 'implantações'}, melhorou, mas ainda tem continuidade e naturalidade para ajustar. hoje eu colocaria algo perto de 5/10"
    return f"entendi. olhando {topic or 'o contexto atual'}, o próximo ganho é continuidade da conversa e menos respostas genéricas"
