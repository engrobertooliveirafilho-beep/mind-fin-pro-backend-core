import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

STORE_PATH = Path("_runtime_state/p19p37c_emotional_continuity.json")
VERSION = "P19P37C_EMOTIONAL_CONTINUITY_REAL"

def _now(): return datetime.now(timezone.utc).isoformat()

def _load(path=STORE_PATH):
    if not path.exists(): return {}
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return {}

def _save(data, path=STORE_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def detect_emotional_signal(text: str) -> Dict[str, Any]:
    lower = str(text or "").lower()
    signals = []
    if any(x in lower for x in ["frustrado", "travou", "não deu", "falhou"]):
        signals.append("friction")
    if any(x in lower for x in ["perfeito", "boa", "consegui", "passou"]):
        signals.append("positive_progress")
    if any(x in lower for x in ["preocupado", "medo", "inseguro"]):
        signals.append("concern")
    return {"signals": signals, "diagnosis": None, "version": VERSION}

def update_emotional_continuity(sender: str, text: str, path=STORE_PATH) -> Dict[str, Any]:
    sender = str(sender or "unknown")
    store = _load(path)
    profile = store.get(sender) or {"sender": sender, "recent_signals": [], "updated_at": _now(), "version": VERSION}
    signal = detect_emotional_signal(text)
    if signal["signals"]:
        profile["recent_signals"].append({"timestamp": _now(), "signals": signal["signals"], "text_preview": str(text)[:160]})
        profile["recent_signals"] = profile["recent_signals"][-20:]
    profile["updated_at"] = _now()
    store[sender] = profile
    _save(store, path)
    return {"sender": sender, "profile": profile, "mode": "SHADOW_ONLY", "version": VERSION}

def attach_emotional_continuity_shadow(ctx: Dict[str, Any] | None = None, sender: str = "", text: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37c_emotional_continuity_real_shadow"] = update_emotional_continuity(sender, text)
    return ctx
