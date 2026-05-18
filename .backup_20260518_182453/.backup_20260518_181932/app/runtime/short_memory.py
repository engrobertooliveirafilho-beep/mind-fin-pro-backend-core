from time import time

_RUNTIME_MEMORY = {}

def remember(user_id: str, topic: str):
    _RUNTIME_MEMORY[user_id] = {
        "topic": topic,
        "ts": time()
    }

def recall(user_id: str):
    item = _RUNTIME_MEMORY.get(user_id)

    if not item:
        return None

    # expira em 120s
    if (time() - item["ts"]) > 120:
        return None

    return item["topic"]
