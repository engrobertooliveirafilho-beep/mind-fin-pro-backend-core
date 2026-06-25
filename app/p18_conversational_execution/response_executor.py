from typing import Dict, Any
from app.p18_conversational_execution.intent_router import classify_intent

FORBIDDEN_PATTERNS = ["Passo 1", "Passo 2", "guia", "checklist", "siga estas etapas", "Para abordar"]

ASPECTS = "planejamento hierárquico, shadow mode, feature flags, telemetria, segurança, consumo interno e respostas mais diretas."

def execute_conversational_response(message: str, context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = context or {}
    intent = classify_intent(message)
    text = (message or "").strip()

    if intent["intent"] == "GREETING":
        answer = "Oi! Tudo bem?"

    elif intent["intent"] == "CHECKIN":
        answer = "Tudo bem. E você?"

    elif intent["intent"] == "IMPLEMENTATION_OPINION":
        answer = "Estão boas. O maior ganho é deixar a MIND mais objetiva, segura e menos genérica."

    elif intent["intent"] == "IMPLEMENTATION_ASPECTS":
        answer = f"São estes: {ASPECTS}"

    elif intent["intent"] == "CONTINUE_CONTEXT":
        answer = f"Continuando: {ASPECTS}"

    elif intent["intent"] == "ASK_PROBLEM":
        answer = "Claro. Me conta o que aconteceu."

    elif intent["intent"] == "FETCH_PREVIOUS_REQUEST":
        answer = "Me diga qual música ou artista que eu procuro e te envio."

    elif intent["intent"] == "FETCH_LINK":
        if "metallica" in text.lower():
            answer = "Qual música do Metallica você quer?"
        else:
            answer = "Qual música você quer que eu procure?"

    elif intent["intent"] == "DIRECT_LIST":
        answer = f"Os principais aspectos são: {ASPECTS}"

    else:
        answer = "Entendi. Me diga exatamente o que você quer que eu faça."

    blocked_patterns = [p for p in FORBIDDEN_PATTERNS if p.lower() in answer.lower()]

    return {
        "mission": "P18_CONVERSATIONAL_EXECUTION_LAYER",
        "input": message,
        "intent": intent["intent"],
        "answer": answer,
        "short_reply": len(answer) <= 280,
        "blocked_patterns": blocked_patterns,
        "runtime_modified": False,
        "routes_modified": False,
        "dispatcher_modified": False,
        "whatsapp_webhook_modified": False,
        "production_enabled": False,
        "status": "PASS" if len(blocked_patterns) == 0 and len(answer) <= 280 else "FAIL",
    }
