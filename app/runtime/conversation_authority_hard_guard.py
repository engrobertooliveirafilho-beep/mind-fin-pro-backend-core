FORBIDDEN_GENERIC_FRAGMENTS = [
    "me dá só o objetivo",
    "entendi. vou responder",
    "bora com calma",
    "como posso ajudar hoje",
    "me diga melhor",
    "pode mandar a dúvida direto",
]

def is_dominant_generic_fallback(text):
    if not text:
        return True
    normalized = str(text).strip().lower()
    if len(normalized) < 3:
        return True
    return any(x in normalized for x in FORBIDDEN_GENERIC_FRAGMENTS)

def sanitize_final_answer(text, replacement=None):
    if replacement is None:
        replacement = "Certo. Vou continuar pelo contexto ativo e te dar o próximo passo direto."
    if is_dominant_generic_fallback(text):
        return replacement
    return str(text).strip()
