import re

INTRO_PATTERNS = [
    "oi! tudo bem",
    "oi, tudo bem",
    "tudo certo por aqui",
    "e você? como estão as coisas",
    "como posso te ajudar",
    "pode me dar mais detalhes"
]

def strip_repeated_intro(text:str)->str:
    out = str(text or "").strip()
    low = out.lower()

    for p in INTRO_PATTERNS:
        if low.startswith(p):
            parts = re.split(r"[.!?]\s+", out, maxsplit=1)
            if len(parts) > 1:
                return parts[1].strip()

    return out

def reset_stale_topic(user_message:str, answer:str)->str:
    return answer

def final_conversation_guard(user_message:str, answer:str)->str:
    out = strip_repeated_intro(
        reset_stale_topic(user_message, answer)
    )

    low = out.lower()
    user_low = (user_message or "").lower()

    banned = [
        "alguma novidade",
        "tem alguma novidade",
        "como estão as coisas",
        "o que você quer saber exatamente",
        "sou a eldora",
        "como posso ajudar",
        "como posso te ajudar hoje",
        "pode me dar mais detalhes"
    ]

    if any(x in low for x in banned):

        if any(x in user_low for x in [
            "oi","ola","olá","bom dia",
            "boa tarde","boa noite",
            "tudo bem","como vc ta",
            "como voce ta","e vc","e você"
        ]):
            return "Tudo certo por aqui 🙂 E você?"

        if any(x in user_low for x in [
            "qual seu nome",
            "quem e voce",
            "quem é você",
            "quem é vc"
        ]):
            return "Sou a Eldora 🙂"

        return "Entendi 🙂 Me fala o ponto principal."

    return out
