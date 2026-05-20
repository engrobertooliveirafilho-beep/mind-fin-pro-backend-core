from app.runtime.response_scorer import score_response
from app.runtime.response_critic import critique_response
from app.runtime.rewrite_engine import rewrite_response

def mature_response(text: str, user_text: str="") -> dict:
    before=score_response(text)
    final=rewrite_response(text,user_text)
    after=score_response(final)
    return {"input": text, "output": final, "before": before, "after": after, "maturity_score": after["score"], "maturity_ready": after["score"] >= 90}
