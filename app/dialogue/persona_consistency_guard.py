PERSONA="eldora_contextual"
def enforce(answer):
    a=(answer or "").lower()
    banned=["como posso ajudar","alguma dúvida específica","alguma duvida especifica","sou a eldora","camada conversacional do mind","runtime estável v2","resumo técnico do mind"]
    if any(x in a for x in banned):
        return False
    return True
