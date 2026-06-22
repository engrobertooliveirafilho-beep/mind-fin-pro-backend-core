import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


STORE_PATH = Path("_runtime_state/p19p36o_relationship_memory.json")
TELEMETRY_PATH = Path("_runtime_state/p19p36o_relationship_memory_telemetry.jsonl")
VERSION = "P19P36O_A_RELATIONSHIP_MEMORY_FOUNDATION"


def relationship_memory_enabled() -> bool:
    return str(os.getenv("P19P36O_RELATIONSHIP_MEMORY_ENABLED", "false")).lower() in {
        "1", "true", "yes", "on"
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_profile(sender: str) -> Dict[str, Any]:
    return {
        "sender": sender,
        "goals": [],
        "projects": [],
        "preferences": [],
        "facts": [],
        "active_topics": [],
        "confidence": {},
        "updated_at": _now(),
        "version": VERSION,
    }


def _load_store(path: Path = STORE_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_store(data: Dict[str, Any], path: Path = STORE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_unique(items: List[str], value: str) -> bool:
    value = str(value or "").strip()
    if not value:
        return False
    if value not in items:
        items.append(value)
        return True
    return False


def _telemetry(sender: str, entity_type: str, value: str, action: str) -> None:
    try:
        TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": _now(),
            "sender": sender,
            "entity_type": entity_type,
            "value": value,
            "action": action,
            "version": VERSION,
        }
        with TELEMETRY_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def extract_relationship_candidates(text: str) -> Dict[str, List[str]]:
    raw = str(text or "").strip()
    lower = raw.lower()

    out = {
        "goals": [],
        "projects": [],
        "preferences": [],
        "facts": [],
        "active_topics": [],
    }

    goal_patterns = [
        r"\bquero\s+(.{3,80})",
        r"\bpretendo\s+(.{3,80})",
        r"\bminha meta (?:é|e)\s+(.{3,80})",
        r"\bmeu objetivo (?:é|e)\s+(.{3,80})",
        r"\bplanejo\s+(.{3,80})",
    ]

    for pattern in goal_patterns:
        m = re.search(pattern, lower)
        if m:
            val = m.group(1).strip(" .!?")
            if val:
                out["goals"].append(val)

    if "emagrecer" in lower or "emagrecimento" in lower:
        out["goals"].append("emagrecer")
        out["active_topics"].append("fitness")

    if "ftmo" in lower:
        out["projects"].append("FTMO")
        out["goals"].append("aprovação FTMO")
        out["active_topics"].append("trader")

    if "mind trader" in lower:
        out["projects"].append("MIND Trader")
        out["active_topics"].append("trader")

    if "eldora" in lower:
        out["projects"].append("Eldora")
        out["active_topics"].append("eldora")

    if "powershell" in lower:
        out["preferences"].append("PowerShell")

    if "whatsapp" in lower:
        out["preferences"].append("WhatsApp")

    fact_patterns = [
        r"\btenho dor (?:no|na|nos|nas|de)?\s*(.{3,60})",
        r"\bestou estudando (?:para|pra)?\s*(.{3,80})",
        r"\btrabalho com\s+(.{3,80})",
    ]

    for pattern in fact_patterns:
        m = re.search(pattern, lower)
        if m:
            val = m.group(1).strip(" .!?")
            if "dor" not in val and pattern.startswith("\\btenho dor"):
                val = "dor " + val
            if val:
                out["facts"].append(val)

    for key in out:
        dedup = []
        for item in out[key]:
            item = str(item).strip()
            if item and item not in dedup:
                dedup.append(item)
        out[key] = dedup

    return out


def update_relationship_memory_shadow(sender: str, text: str, path: Path = STORE_PATH) -> Dict[str, Any]:
    sender = str(sender or "unknown").strip() or "unknown"

    store = _load_store(path)
    profile = store.get(sender) or _empty_profile(sender)

    candidates = extract_relationship_candidates(text)
    changed = False

    for field in ["goals", "projects", "preferences", "facts", "active_topics"]:
        profile.setdefault(field, [])
        for value in candidates.get(field, []):
            if _append_unique(profile[field], value):
                changed = True
                _telemetry(sender, field[:-1] if field.endswith("s") else field, value, "added")

    profile.setdefault("confidence", {})
    for field in ["goals", "projects", "preferences", "facts", "active_topics"]:
        if candidates.get(field):
            profile["confidence"][field] = "LOW_RULE_BASED"

    profile["updated_at"] = _now()
    profile["version"] = VERSION

    store[sender] = profile
    _save_store(store, path)

    return {
        "enabled": relationship_memory_enabled(),
        "changed": changed,
        "sender": sender,
        "profile": profile,
        "candidates": candidates,
        "mode": "SHADOW_ONLY",
        "version": VERSION,
    }


def get_relationship_memory(sender: str, path: Path = STORE_PATH) -> Dict[str, Any]:
    sender = str(sender or "unknown").strip() or "unknown"
    store = _load_store(path)
    return store.get(sender) or _empty_profile(sender)
