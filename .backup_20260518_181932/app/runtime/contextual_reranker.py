def contextual_rerank(rows, query):
    q=(query or "").lower()
    scored=[]
    for r in rows:
        msg=(r.get("message") or "").lower()
        bonus=0.0
        for token in q.split():
            if len(token)>3 and token in msg: bonus+=0.03
        r["contextual_score"]=float(r.get("score") or 0)+bonus
        scored.append(r)
    return sorted(scored,key=lambda x:x.get("contextual_score",0),reverse=True)
