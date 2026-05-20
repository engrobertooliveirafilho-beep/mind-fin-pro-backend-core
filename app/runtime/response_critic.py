from app.runtime.response_scorer import score_response

def critique_response(text: str, user_text: str="") -> dict:
    s=score_response(text)
    fixes=[]
    if "fallback_language" in s["flags"]:
        fixes.append("remover linguagem de falha/fallback")
    if "too_short" in s["flags"]:
        fixes.append("aumentar utilidade prática")
    if "low_operational_structure" in s["flags"]:
        fixes.append("adicionar próximo passo concreto")
    return {"score": s["score"], "flags": s["flags"], "fixes": fixes}
