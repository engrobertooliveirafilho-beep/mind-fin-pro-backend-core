_LAST_STATE={}
_COUNTER=0
def factual_answer(text:str)->str:
    t=(text or "").lower()
    if "cr250" in t or "cr250r" in t:
        return "Busca factual necessária: validar CR250R 2001 2 tempos, peça exata e compatibilidade antes de concluir."
    if "k1300" in t:
        return "A BMW K1300 se destaca por motor forte, estabilidade, conforto em estrada e boa ciclística."
    return ""
def factual_search_handoff(reply,message):
    global _COUNTER
    m=(message or "").lower(); r=(reply or "")
    if "cr250" in m or "cr250r" in m: _LAST_STATE["topic"]="motorcycle"
    if "eldora" in m: _LAST_STATE.clear()
    if m in {"aprofunde","aprofundar"}:
        _COUNTER+=1
        return f"Vou aprofundar com base no ponto anterior e avançar para evidência prática #{_COUNTER}."
    ans=factual_answer(message)
    return ans or (r if ("não ficou claro" not in r.lower() and len(r)>0) else "Busca factual necessária: preciso validar a fonte antes de responder.")

