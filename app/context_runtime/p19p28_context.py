from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

STORE = Path("_runtime_state/p19p28_context_by_sender.json")

def _load():
    if STORE.exists():
        try:
            return json.loads(STORE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def _save(data):
    STORE.parent.mkdir(parents=True, exist_ok=True)
    STORE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def bind(sender: str, domain: str, text: str):
    data = _load()
    sid = sender or "unknown"
    data[sid] = {
        "active_domain": domain,
        "last_text": text or "",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    _save(data)

def get(sender: str):
    return _load().get(sender or "unknown", {})
