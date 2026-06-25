# wrapper compatível com APIs antigas e novas
from app.runtime.short_memory import recall as _recall

def safe_recall(sender_id):
    try:
        return _recall(sender_id)
    except Exception:
        return None

def safe_recall_with_fallback(sender_id):
    ctx = safe_recall(sender_id)
    if not ctx:
        return ""
    return str(ctx)
