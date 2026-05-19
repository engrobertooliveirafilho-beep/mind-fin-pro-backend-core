import re

BANNED_PATTERNS = [
    r"eu sou a eldora",
    r"camada conversacional do mind",
    r"minha função é entender seu contexto",
    r"como ia",
    r"informação registrada",
    r"estou processando"
]

IDENTITY_ALLOWED = re.compile(
    r"(quem é você|quem e voce|se apresente|qual seu nome|você é quem|vc é quem)",
    re.I
)

def guard_identity_fallback(user_text:str,response:str)->str:
    u=(user_text or "").strip().lower()
    r=(response or "").strip()

    if IDENTITY_ALLOWED.search(u):
        return r

    low=r.lower()

    leaked=any(re.search(p,low) for p in BANNED_PATTERNS)

    if leaked:
        if any(x in u for x in ["oi","olá","ola","eai","e aí"]):
            return "Oi, Roberto. Como você está? O que vamos resolver agora?"

        if "tudo bem" in u:
            return "Tudo certo por aqui. E você, como está?"

        if u in ["sim","aham","ok","blz","beleza","isso"]:
            return "Perfeito. Me fala o próximo passo ou o que você quer testar."

        if "simulador" in u:
            return "Boa. Isso pode ajudar bastante a amadurecer conversa, continuidade e respostas menos robóticas. Como você imagina esse simulador?"

        return "Entendi. Continua — estou acompanhando o contexto."

    return r
