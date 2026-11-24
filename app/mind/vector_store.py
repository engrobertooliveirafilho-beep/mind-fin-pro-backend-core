import math
from threading import RLock
_VECTORS = {}
_LOCK = RLock()

def _key(user_id, session_id):
    if any(not isinstance(x,str) or not x.strip() for x in (user_id,session_id)):
        raise ValueError('Explicit scope required')
    return user_id, session_id

def _normalize(values):
    v = tuple(float(x) for x in values)
    if not v or not all(math.isfinite(x) for x in v):
        raise ValueError('Invalid vector')
    scale = max(map(abs,v))
    if not scale:
        raise ValueError('Zero vector')
    v = tuple(x/scale for x in v)
    norm = math.hypot(*v)
    return tuple(x/norm for x in v)

def add_vector(text, embedding, *, user_id, session_id):
    key = _key(user_id,session_id)
    v = _normalize(embedding)
    with _LOCK:
        _VECTORS.setdefault(key,[]).append((text,v))

def search_vectors(query_embedding, top_k=5, *, user_id, session_id):
    key = _key(user_id,session_id)
    q = _normalize(query_embedding)
    if type(top_k) is not int or not 1 <= top_k <= 100:
        raise ValueError('Invalid limit')
    with _LOCK:
        rows = list(_VECTORS.get(key,[]))
    scored = [(sum(x*y for x,y in zip(q,v)),text,v) for text,v in rows if len(v)==len(q)]
    scored.sort(key=lambda row: row[0],reverse=True)
    return [dict(text=t,embedding=list(v)) for _,t,v in scored[:top_k]]
