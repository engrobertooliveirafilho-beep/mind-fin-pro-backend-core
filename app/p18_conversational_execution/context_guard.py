from typing import Dict, Any

BAD_CONTEXT_TERMS = [
    "preço", "frete", "oem", "estriado", "pedal", "compatibilidade",
    "peça", "encaixe", "geometria", "devolução"
]

def detect_context_contamination(user_message: str, answer: str, active_topic: str = "") -> Dict[str, Any]:
    text = (answer or "").lower()
    hits = [t for t in BAD_CONTEXT_TERMS if t in text]

    contaminated = False
    if active_topic and active_topic.lower() in {"eldora", "fluidez", "cac", "sono"} and hits:
        contaminated = True

    return {
        "contaminated": contaminated,
        "hits": hits,
        "active_topic": active_topic,
        "status": "BLOCK" if contaminated else "PASS",
    }

def safe_topic_from_message(message: str) -> str:
    text = (message or "").lower()
    if "eldora" in text or "fluidez" in text:
        return "fluidez"
    if "cac" in text:
        return "cac"
    if "dormi" in text or "sono" in text:
        return "sono"
    return "general"
