from app.runtime.semantic_answer_engine import semantic_answer

def route_semantic_whatsapp(message: str, sender_id: str = "default") -> str:
    return semantic_answer(message, sender_id).get("answer", "")

def semantic_whatsapp_payload(message: str, sender_id: str = "default") -> dict:
    return semantic_answer(message, sender_id)
