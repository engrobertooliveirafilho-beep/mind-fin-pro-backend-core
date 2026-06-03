import hashlib

_LAST_BY_USER = {}

def _hash(text: str) -> str:
    return hashlib.sha1((text or "").strip().lower().encode()).hexdigest()[:12]

def remember_response(user_id: str, answer: str):
    history = _LAST_BY_USER.setdefault(user_id, [])
    history.append({"hash": _hash(answer), "answer": answer})
    _LAST_BY_USER[user_id] = history[-5:]

def is_repeated(user_id: str, answer: str) -> bool:
    h = _hash(answer)
    return any(item["hash"] == h for item in _LAST_BY_USER.get(user_id, []))

def short_message_type(message: str) -> str:
    t = (message or "").strip().lower()
    if t in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]: return "greeting"
    if t in ["ok", "certo", "beleza", "show", "fechado"]: return "ack"
    if "repete" in t or "porque vc repete" in t: return "repetition_complaint"
    if t.startswith("como fazer") or "como posso" in t: return "how_to"
    if t in ["prosseguir", "continua", "segue"]: return "continue"
    return "normal"
