class ScoreResult(dict):
    def __getattr__(self,k): return self[k]
from app.runtime.intent_arbitration_priority_engine import classify_intent
def score_message(user_text:str, answer:str):
    intent=classify_intent(user_text)["intent"]; a=(answer or "").lower()
    leak=int(any(x in a for x in ["mind","eldora","memória contextual","memoria contextual","voc├","­ƒ"]))
    fallback=int("não entendi" in a or "não ficou claro" in a)
    handback=int("qual camada" in a or "você vai mexer" in a)
    duplication=int(((answer or "").count("\n")>3) or ((user_text or "").lower() in a))
    size_ok=len(answer or "")<=220
    score=max(0,10-leak*3-fallback*4-handback*3-duplication*2-(0 if size_ok else 2))
    return ScoreResult(intent=intent,score=score,leak=leak,fallback=fallback,duplication=duplication,size_ok=size_ok,chars=len(answer or ""))
def score_batch(items):
    scores=[score_message(x.get("message",""),x.get("reply","")) if isinstance(x,dict) else score_message(x[0],x[1]) for x in items]; return {"passed":all(s.score>=6 and s.fallback==0 for s in scores),"scores":scores}




