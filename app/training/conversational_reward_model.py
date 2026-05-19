from app.humanization.human_conversation_runtime import score_response,human_reply
def score(prompt,response): return score_response(prompt,response)
def critique(prompt,response):
    s=score_response(prompt,response)
    notes=[]
    if s["identity_leak"]: notes.append("identity fallback leakage")
    if s["score"]<95: notes.append("melhorar naturalidade, continuidade e resposta direta")
    return {"score":s,"notes":notes}
def rewrite(prompt,response):
    c=critique(prompt,response)
    return human_reply(prompt) if c["notes"] else response
def best_response(prompt):
    a=human_reply(prompt); b=rewrite(prompt,a)
    return b if score_response(prompt,b)["score"]>=score_response(prompt,a)["score"] else a
