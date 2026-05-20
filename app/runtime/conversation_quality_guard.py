import re

INTRO_PATTERNS=[
    "oi! tudo bem",
    "oi, tudo bem",
    "tudo certo por aqui",
    "e você?",
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
    if any(b in low for b in banned):
    if any(x in (user_message or "").lower() for x in ["oi","ola","olá","bom dia","boa tarde","boa noite","tudo bem","como vc ta","como voce ta","e vc","e você"]):
        return "Tudo certo por aqui 🙂 E você?"
    return "Entendi 🙂 Me fala o ponto principal e seguimos daqui."

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
    out = reset_stale_topic(user_message, answer)
    out = strip_repeated_intro(out)

    banned = [
        "você tem alguma informação adicional",
        "alguma novidade",
        "tem alguma novidade",
        "como estão as coisas",
        "o que você quer saber exatamente",
        "sou a eldora",
        "como posso ajudar",
        "como posso te ajudar hoje",
        "pode me dar mais detalhes"
    ]

    low = out.lower()
    user_low = (user_message or "").lower()

    if any(b in low for b in banned):

        casual = any(x in user_low for x in [
            "oi","ola","olá","bom dia","boa tarde","boa noite",
            "tudo bem","como vc ta","como voce ta",
            "e vc","e você"
        ])

        identity = any(x in user_low for x in [
            "qual seu nome","quem e voce","quem é você","quem é vc"
        ])

        if identity:
            return "Sou a Eldora 🙂"

        if casual:
            return "Tudo certo por aqui 🙂 E você?"

        return "Entendi 🙂 Me fala o ponto principal e seguimos daqui."

    return out