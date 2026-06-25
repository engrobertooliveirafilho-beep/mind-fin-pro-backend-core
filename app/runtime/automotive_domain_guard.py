def is_automotive_aks_context(message: str, context: str = "") -> bool:
    text = f"{message or ''} {context or ''}".lower()
    strong_terms = [
        "mercedes", "classe a", "w168", "aks", "semi automatica", "semi automática",
        "atuador", "embreagem", "marcha", "cambio", "câmbio"
    ]
    symptom = (
        ("desligado" in text and "ligado" in text and "marcha" in text)
        or ("ligado" in text and ("não entra" in text or "nao entra" in text) and "marcha" in text)
    )
    return symptom or any(t in text for t in strong_terms)


def automotive_domain_override(message: str, routed_intent=None, context: str = ""):
    if not is_automotive_aks_context(message, context):
        return routed_intent

    if isinstance(routed_intent, dict):
        routed_intent = dict(routed_intent)
        routed_intent["domain"] = "automotive"
        routed_intent["intent"] = routed_intent.get("intent") or "automotive_diagnosis"
        routed_intent["automotive_context"] = "mercedes_classe_a_aks"
        routed_intent["blocked_domain"] = "agricultural_equipment"
        return routed_intent

    return {
        "intent": "automotive_diagnosis",
        "domain": "automotive",
        "automotive_context": "mercedes_classe_a_aks",
        "blocked_domain": "agricultural_equipment",
        "confidence": 0.98,
    }


def suppress_agricultural_contamination(message: str, answer: str, context: str = "") -> str:
    text = f"{message or ''} {context or ''}".lower()
    out = str(answer or "")

    if not is_automotive_aks_context(text):
        return out

    bad_terms = [
        "equipamento agrícola",
        "equipamento agricola",
        "agrícola",
        "agricola",
        "trator",
        "tractor",
    ]

    if any(t in out.lower() for t in bad_terms):
        return (
            "Isso aponta para o acionamento da embreagem/AKS do Mercedes Classe A. "
            "Se desligado entra marcha e ligado não entra, a embreagem provavelmente não está desacoplando totalmente. "
            "Prioridade: atuador AKS, curso da haste, garfo/rolamento, sangria/calibração e adaptação do sistema."
        )

    return out
