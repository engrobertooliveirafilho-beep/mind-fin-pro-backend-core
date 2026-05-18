import time

_embedding_cache = {}

def cached_embed(provider, text):
    key = (text or "").strip()[:2000]
    if not key:
        return None

    now = time.time()

    if key in _embedding_cache:
        item = _embedding_cache[key]
        if now - item["ts"] < 3600:
            return item["emb"]

    emb = provider.embed(key)

    _embedding_cache[key] = {
        "emb": emb,
        "ts": now
    }

    return emb
