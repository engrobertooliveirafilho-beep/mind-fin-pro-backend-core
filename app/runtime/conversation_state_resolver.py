import unicodedata, re
from app.runtime.decision_memory import get_state

FOLLOWUP={"aprofunde","continua","prossiga","e depois","explica melhor","detalha","explique melhor"}
TROUBLE={"erro","falhou","deu errado","nao funcionou","quebrou","implantacao"}
TASK={"analise","verifique","busque","calcule","confira","execute"}
SOCIAL={"oi","ola","tudo bem","quem e vc","quem e voce","como vc esta","como voce esta","bom dia","boa tarde","boa noite","voce esta funcionando","qual seu papel aqui","qual e seu papel","o que voce faz","quem e a eldora"}

def _norm(msg:str)->str:
    s=(msg or "").lower().strip()
    s="".join(c for c in unicodedata.normalize("NFD",s) if unicodedata.category(c)!="Mn")
    s=re.sub(r"[^a-z0-9\s]"," ",s)
    return " ".join(s.split())

def _has(m, items):
    return any(x in m for x in items)

def resolve(sender_id,msg):
    s=get_state(sender_id); m=_norm(msg)
    if _has(m,TROUBLE): return "TROUBLESHOOTING",s
    if _has(m,FOLLOWUP): return "FOLLOWUP",s
    if _has(m,TASK): return "TASK",s
    if _has(m,SOCIAL): return "SOCIAL",s
    return "AMBIGUOUS",s
