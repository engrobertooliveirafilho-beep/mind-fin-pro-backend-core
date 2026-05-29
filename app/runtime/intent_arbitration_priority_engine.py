import re, unicodedata

PRIORITY = [
    "CALCULATION",
    "FACTUAL_QUESTION",
    "BUYING_ADVICE",
    "TASK_VERIFICATION",
    "SOCIAL",
    "FOLLOWUP",
    "OPEN_LOOP",
    "AMBIGUOUS_FALLBACK",
]

def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s)

def classify_intent(text: str) -> dict:
    t = _norm(text)
    if not t:
        return {"intent": "AMBIGUOUS_FALLBACK", "confidence": 0.0, "reason": "empty"}

    if re.fullmatch(r"[0-9\s\+\-\*\/\(\)\.,]+", t) and re.search(r"\d", t) and re.search(r"[\+\-\*\/]", t):
        return {"intent": "CALCULATION", "confidence": 0.99, "reason": "math_expression"}

    social_exact = {
        "oi","ola","olá","bom dia","boa tarde","boa noite","tudo bem","tudo bem?",
        "eu to bem","eu tô bem","eu estou bem","to bem","tô bem","estou bem","beleza"
    }
    if t in {_norm(x) for x in social_exact}:
        return {"intent": "SOCIAL", "confidence": 0.95, "reason": "social_exact"}

    buying = r"\b(comprar|compra|vale a pena|moto|carro|veiculo|veiculo|bmw|honda|yamaha|k1300|qualidades|pontos fortes|melhores|defeitos|problemas)\b"
    question = r"\b(qual|quais|quanto|quem|onde|quando|como|porque|por que|melhor|melhores|pontos fortes|vale a pena)\b"
    if re.search(buying, t):
        return {"intent": "BUYING_ADVICE", "confidence": 0.93, "reason": "buying_product_vehicle"}

    if re.search(question, t):
        return {"intent": "FACTUAL_QUESTION", "confidence": 0.88, "reason": "question_word"}

    

    if t in {"e depois?", "e depois", "aprofunde", "continue", "prossiga", "explique melhor"}:
        return {"intent": "FOLLOWUP", "confidence": 0.82, "reason": "followup"}

    if len(t.split()) <= 3:
        return {"intent": "OPEN_LOOP", "confidence": 0.55, "reason": "short_open_loop"}

    return {"intent": "AMBIGUOUS_FALLBACK", "confidence": 0.30, "reason": "no_class"}


# LAST PRIORITY: TASK VERIFICATION
if re.search(r"\b(verificar|validar|testar|corrigir|executar|analisar|auditar)\b", t):
    return {"intent": "TASK_VERIFICATION", "confidence": 0.70, "reason": "task_word_low_priority"}

