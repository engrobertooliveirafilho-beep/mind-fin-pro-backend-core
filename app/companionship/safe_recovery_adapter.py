from __future__ import annotations

import importlib
from typing import Any, Dict, List

# P19P36G_SAFE_RECOVERY_ADAPTER
# Shadow-only adapter: não altera resposta, não altera fluxo vivo.
# Apenas tenta recuperar sinais de módulos existentes com segurança.

RECOVERED_MODULES = [
    "app.runtime.followup_unified_resolver",
    "app.runtime.generic_topic_memory_engine",
    "app.runtime.memory_adapter",
    "app.runtime.memory_store",
    "app.vision.vision_memory_store",
]

def safe_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

def collect_recovered_context(sender: str, text: str, base_ctx: Dict[str, Any] | None = None) -> Dict[str, Any]:
    ctx = dict(base_ctx or {})
    try:
        ctx = collect_memory_shadow(sender, text, ctx)
    except Exception:
        pass
    recovered: List[Dict[str, Any]] = []

    for module_name in RECOVERED_MODULES:
        mod = safe_import(module_name)
        if not mod:
            continue

        payload = {"module": module_name, "signals": {}}

        for fn_name in ["get", "resolve", "recall", "load", "get_context", "get_memory", "get_profile"]:
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                try:
                    payload["signals"][fn_name] = str(fn(sender))[:500]
                except TypeError:
                    try:
                        payload["signals"][fn_name] = str(fn(sender, text))[:500]
                    except Exception:
                        pass
                except Exception:
                    pass

        if payload["signals"]:
            recovered.append(payload)

    ctx["recovered_shadow_context"] = recovered
    return ctx

def enrich_reply_shadow(sender: str, text: str, base_ctx: Dict[str, Any], reply: str) -> str:
    # Shadow mode: não modifica a resposta.
    return reply
# /P19P36G_SAFE_RECOVERY_ADAPTER


# P19P36H_SHADOW_TELEMETRY
import json
from pathlib import Path
from datetime import datetime, timezone

TELEMETRY = Path("_runtime_state/p19p36h_recovery_shadow_telemetry.jsonl")

def _safe_json_default(obj):
    try:
        return str(obj)
    except Exception:
        return "<unserializable>"

def record_shadow_telemetry(sender: str, text: str, ctx: dict, reply: str) -> None:
    try:
        TELEMETRY.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sender": sender or "unknown",
            "text": (text or "")[:300],
            "active_domain": (ctx or {}).get("active_domain"),
            "active_subject": (ctx or {}).get("active_subject"),
            "recovered_shadow_context_count": len((ctx or {}).get("recovered_shadow_context", [])),
            "recovered_shadow_context": (ctx or {}).get("recovered_shadow_context", []),
            "memory_shadow": (ctx or {}).get("p19p36k_memory_shadow", {}),
            "reply_preview": (reply or "")[:300],
        }
        with TELEMETRY.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, default=_safe_json_default) + "\n")
    except Exception:
        pass
# /P19P36H_SHADOW_TELEMETRY


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
