from pathlib import Path

p = Path("app/companionship/safe_recovery_adapter.py")
s = p.read_text(encoding="utf-8")

insert = r'''

# P19P36K_SAFE_MEMORY_ADAPTER_V2
def _p19p36k_normalize_memory_item(x):
    try:
        if isinstance(x, str):
            return x.strip()
        return str(x).strip()
    except Exception:
        return ""

def _p19p36k_get_memory_store():
    try:
        from app.runtime.memory_store import SimpleMemoryStore
        return SimpleMemoryStore()
    except Exception:
        return None

def remember_user_message(sender: str, text: str) -> bool:
    try:
        t = str(text or "").strip()
        if not t:
            return False
        store = _p19p36k_get_memory_store()
        if not store:
            return False
        store.save(sender or "unknown", t)
        return True
    except Exception:
        return False

def recall_user_history(sender: str, limit: int = 8):
    try:
        store = _p19p36k_get_memory_store()
        if not store:
            return []
        items = store.recall(sender or "unknown", int(limit))
        if not isinstance(items, list):
            return []
        clean = []
        for x in items:
            v = _p19p36k_normalize_memory_item(x)
            if v:
                clean.append(v)
        return clean[-int(limit):]
    except Exception:
        return []

def collect_memory_shadow(sender: str, text: str, base_ctx: dict | None = None) -> dict:
    ctx = dict(base_ctx or {})
    remembered = remember_user_message(sender, text)
    history = recall_user_history(sender, 8)

    ctx["p19p36k_memory_shadow"] = {
        "remembered": remembered,
        "history_count": len(history),
        "history": history,
    }
    return ctx
# /P19P36K_SAFE_MEMORY_ADAPTER_V2
'''

if "P19P36K_SAFE_MEMORY_ADAPTER_V2" not in s:
    s += insert

# Inserir memória shadow dentro do collect_recovered_context
old = '''def collect_recovered_context(sender: str, text: str, base_ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(base_ctx or {})
    recovered: List[Dict[str, Any]] = []
'''

new = '''def collect_recovered_context(sender: str, text: str, base_ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(base_ctx or {})
    try:
        ctx = collect_memory_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []
'''

if "ctx = collect_memory_shadow(sender, text, ctx)" not in s:
    if old not in s:
        raise SystemExit("collect_recovered_context block not found")
    s = s.replace(old, new, 1)

# Expandir telemetria para incluir memory shadow
old2 = '''            "recovered_shadow_context_count": len((ctx or {}).get("recovered_shadow_context", [])),
            "recovered_shadow_context": (ctx or {}).get("recovered_shadow_context", []),
            "reply_preview": (reply or "")[:300],
'''

new2 = '''            "recovered_shadow_context_count": len((ctx or {}).get("recovered_shadow_context", [])),
            "recovered_shadow_context": (ctx or {}).get("recovered_shadow_context", []),
            "memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),
            "reply_preview": (reply or "")[:300],
'''

if '"memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),' not in s:
    if old2 not in s:
        raise SystemExit("telemetry block not found")
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding="utf-8")
print("P19P36K_SAFE_MEMORY_ADAPTER_PATCH_OK")
