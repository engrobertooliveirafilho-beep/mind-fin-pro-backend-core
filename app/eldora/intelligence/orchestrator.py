import os, re

def normalize_input(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())

def classify_intent(text: str) -> str:
    t = text.lower()
    if "pdf" in t or "documento" in t: return "document_explain"
    if "lotofacil" in t or "lotofácil" in t: return "lotofacil_report"
    if "estudar" in t or "aula" in t: return "study"
    return "general"

def retrieve_context(query: str) -> dict:
    return {"retrieval_ready": True, "sources": [], "context": ""}

def select_model_by_cost(intent: str) -> dict:
    return {"provider": "openai" if os.getenv("OPENAI_API_KEY") else "fallback", "model": "cost_aware_default", "llm_real_declared": bool(os.getenv("OPENAI_API_KEY"))}

def quality_gate(answer: str) -> dict:
    blocked = not answer or len(answer.strip()) < 3
    return {"passed": not blocked, "blocked": blocked}

def respond(payload: dict) -> dict:
    text = normalize_input(payload.get("text", ""))
    intent = classify_intent(text)
    retrieval = retrieve_context(text)
    model = select_model_by_cost(intent)
    answer = f"Resposta Eldora pronta para intent={intent}. Próximo passo operacional definido com segurança."
    qg = quality_gate(answer)
    return {"intent": intent, "answer": answer, "retrieval": retrieval, "model": model, "quality_gate": qg}
