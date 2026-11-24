from datetime import datetime, timezone
from threading import RLock

_STORE = {}
_LOCK = RLock()

def _key(user_id, session_id):
    if any(not isinstance(x,str) or not x.strip() for x in (user_id,session_id)):
        raise ValueError('Explicit identity and session required')
    return user_id, session_id

def add_message(user_id, session_id, role, content, backend=None):
    if backend not in (None,'memory'):
        raise ValueError('Only offline memory supported')
    key = _key(user_id,session_id)
    if role not in ('user','mind','tool','assistant','system') or not isinstance(content,str):
        raise ValueError('Invalid message')
    with _LOCK:
        hist = _STORE.setdefault(key,[])
        hist.append(dict(role=role,content=content,ts=datetime.now(timezone.utc).isoformat()))
        return [dict(m) for m in hist]

def get_history(user_id, session_id, limit=50, backend=None):
    if backend not in (None,'memory') or type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError('Invalid backend or limit')
    key = _key(user_id,session_id)
    with _LOCK:
        return [dict(m) for m in _STORE.get(key,[])[-limit:]]
