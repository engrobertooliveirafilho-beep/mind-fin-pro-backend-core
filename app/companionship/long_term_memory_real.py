import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

STORE_PATH = Path("_runtime_state/p19p37d_long_term_memory_real.json")
VERSION = "P19P37D_LONG_TERM_MEMORY_REAL"

def _now(): return datetime.now(timezone.utc).isoformat()

def consolidate_long_term_memory(sender: str, ctx: Dict[str, Any] | None = None, path: Path = STORE_PATH) -> Dict[str, Any]:
    sender = str(sender or "unknown")
    ctx = dict(ctx or {})
    try:
        store = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        store = {}

    item = store.get(sender) or {
        "sender": sender,
        "stable_goals": [],
        "stable_projects": [],
        "stable_constraints": [],
        "weekly_summary": "",
        "monthly_summary": "",
        "last_consolidated_at": "",
        "version": VERSION,
    }

    dt = ctx.get("p19p37a_digital_twin_real_shadow", {}).get("profile", {}) or {}
    for g in dt.get("goals", []) or []:
        if g not in item["stable_goals"]: item["stable_goals"].append(g)
    for p in dt.get("projects", []) or []:
        if p not in item["stable_projects"]: item["stable_projects"].append(p)
    for c in dt.get("constraints", []) or []:
        if c not in item["stable_constraints"]: item["stable_constraints"].append(c)

    item["weekly_summary"] = "; ".join(item["stable_goals"][:5] + item["stable_projects"][:5])
    item["monthly_summary"] = item["weekly_summary"]
    item["last_consolidated_at"] = _now()

    store[sender] = item
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"sender": sender, "memory": item, "mode": "SHADOW_ONLY", "version": VERSION}

def attach_long_term_memory_shadow(ctx: Dict[str, Any] | None = None, sender: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37d_long_term_memory_real_shadow"] = consolidate_long_term_memory(sender, ctx)
    return ctx
