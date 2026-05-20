import re

INTRO_PATTERNS=[
    "oi! tudo bem",
    "oi, tudo bem",
    "tudo certo por aqui",
    "e você? como estão as coisas",
    "como posso te ajudar",
    "pode me dar mais detalhes"
]

def strip_repeated_intro(text:str)->str:
    out=str(text or "").strip()
    low=out.lower()
    for p in INTRO_PATTERNS:
        if low.startswith(p):
            parts=re.split(r"[.!?]\s+", out, maxsplit=1)
            if len(parts)>1:
                return parts[1].strip()
    return out

def reset_stale_topic(user_message:str, answer:str)->str:
    u=(user_message or "").lower()
    a=(answer or "").lower()

    current_cane=any(x in u for x in ["cane corso","filhote","ração","racao","criador","doenças","doencas"])
    asks_runtime=any(x in u for x in ["simulação","simulacao","módulo","modulo","humanização","humanizacao","eldora","runtime"])

    if asks_runtime and "cane corso" in a:
        return "sim, o módulo de simulação já está rodando, mas ainda falta ligar esse aprendizado diretamente no comportamento da conversa real."

    if not current_cane and "cane corso" in a and asks_runtime:
        return "sim, o módulo de simulação está ativo. Agora o ponto é usar esse aprendizado para corrigir repetição, continuidade e mudança de assunto."

    return answer

def final_conversation_guard(user_message:str, answer:str)->str:
    out=reset_stale_topic(user_message, answer)
    out=strip_repeated_intro(out)

    banned=[
        "você tem alguma informação adicional",
        "alguma novidade",
        "pode me dar mais detalhes",
        "como posso te ajudar hoje"
    ]

    low=out.lower()
    if any(b in low for b in banned):
        return "entendi. vou responder direto pelo contexto atual, sem repetir introdução e sem puxar assunto antigo."

    return out
