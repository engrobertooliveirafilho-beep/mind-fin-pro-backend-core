from app.runtime.intent_arbitration_priority_engine import classify_intent

BAD = ["não entendi", "mind", "eldora", "como posso ajudar hoje"]

def score_message(user_text: str, answer: str) -> dict:
    intent = classify_intent(user_text)["intent"]
    a = (answer or "").lower()
    leak = int(any(x in a for x in ["mind", "eldora"]))
    fallback = int("não entendi" in a)
    duplication = int(answer.count("\n") > 3)
    size_ok = len(answer) <= 220
    score = 10 - leak*3 - fallback*4 - duplication*1 - (0 if size_ok else 2)
    return {"intent": intent, "score": max(score,0), "leak": leak, "fallback": fallback, "duplication": duplication, "size_ok": size_ok, "chars": len(answer)}
