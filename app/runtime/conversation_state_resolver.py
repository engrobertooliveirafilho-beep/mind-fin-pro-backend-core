from app.runtime.decision_memory import get_state

FOLLOWUP = {"aprofunde","continua","prossiga","e depois","explica melhor","detalha","explique melhor"}
TROUBLE = {"erro","falhou","deu errado","não funcionou","nao funcionou","quebrou","implantação","implantacao"}
SOCIAL_EXACT = {"oi","olá","ola","tudo bem","quem é vc","quem é você","como vc está","como você está","bom dia","boa tarde","boa noite","você está funcionando","voce esta funcionando","qual seu papel aqui","qual é seu papel","qual e seu papel","o que você faz","o que voce faz","quem é a eldora","quem e a eldora"}
TASK = {"analise","verifique","busque","calcule","confira","execute"}

def _norm(msg: str) -> str:
    return " ".join((msg or "").lower().strip().split())

def _contains_phrase(msg: str, phrases: set[str]) -> bool:
    return any(p in msg for p in phrases)

def _exact_or_phrase(msg: str, phrases: set[str]) -> bool:
    return msg in phrases

def resolve(sender_id, msg):
    s = get_state(sender_id)
    m = _norm(msg)

    # prioridade correta: erro/follow-up/task antes de social
    if _contains_phrase(m, TROUBLE):
        return "TROUBLESHOOTING", s
    if _contains_phrase(m, FOLLOWUP):
        return "FOLLOWUP", s
    if _contains_phrase(m, TASK):
        return "TASK", s
    if _exact_or_phrase(m, SOCIAL_EXACT):
        return "SOCIAL", s

    return "AMBIGUOUS", s

