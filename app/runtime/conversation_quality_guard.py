import re

INTRO_PATTERNS = [
    "oi! tudo bem",
    "oi, tudo bem",
    "tudo certo por aqui",
    "como posso te ajudar",
    "pode me dar mais detalhes"
]

TECH_TERMS = [
    "history_count",
    "persistent_memory_count",
    "retrieval_provider",
    "retrieval provider",
    "runtime",
    "camada",
    "memória persistente",
    "memoria persistente",
    "context fusion",
    "mind",
    "retrieval",
    "webhook",
    "handler"
]

SOCIAL_HINTS = [
    "mais fluida",
    "fluida",
    "como vc ta",
    "como voce ta",
    "tudo bem",
    "o que achou",
    "vc tem novidade",
    "e vc",
    "e você",
    "o que especifico",
    "como te deixo"
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

    social_mode = any(x in user_low for x in SOCIAL_HINTS)
    leaking_tech = any(x in low for x in TECH_TERMS)

    if social_mode and leaking_tech:
        return (
            "Acho que para eu ficar mais fluida, o principal é conversar de forma mais natural, "
            "lembrar melhor do contexto e responder sem parecer repetitiva 🙂 "
            "Você percebeu algo específico que te incomodou?"
        )

    banned = [
        "alguma novidade",
        "como estão as coisas",
        "sou a eldora",
        "como posso ajudar",
        "pode me dar mais detalhes",
        "o que você quer saber exatamente"
    ]

    if any(x in low for x in banned):
        return "Tudo certo por aqui 🙂 E você?"

    return out
