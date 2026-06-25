from app.runtime.memory_store import SimpleMemoryStore

_memory = SimpleMemoryStore()

FOLLOWUP_KEYS = [
    "como eu faço",
    "como faço",
    "e depois",
    "explique melhor",
    "continue",
    "detalhe",
    "aprofundar"
]

def is_followup(text: str):
    t = (text or "").lower()
    return any(k in t for k in FOLLOWUP_KEYS)

def resolve_followup(sender_id: str, text: str):
    if not is_followup(text):
        _memory.save(sender_id, text)
        return None

    ctx = _memory.recall(sender_id, limit=8)

    if not ctx:
        return "Preciso do contexto anterior para continuar a conversa."

    context_block = "\n".join(ctx)

    return (
        "CONTEXTO ATIVO:\n"
        f"{context_block}\n\n"
        "EXPANSÃO:\n"
        "Vou continuar exatamente do ponto anterior sem reiniciar o tema."
    )
