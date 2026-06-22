import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

STORE_PATH = Path("_runtime_state/p19p37a_digital_twin_real.json")
VERSION = "P19P37A_DIGITAL_TWIN_REAL"

def enabled() -> bool:
    return str(os.getenv("P19P37_DIGITAL_TWIN_ENABLED", "false")).lower() in {"1","true","yes","on"}

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _load(path: Path = STORE_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _save(data: Dict[str, Any], path: Path = STORE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _profile(sender: str) -> Dict[str, Any]:
    return {
        "sender": sender,
        "goals": [],
        "projects": [],
        "preferences": [],
        "constraints": [],
        "behavior_signals": [],
        "emotional_signals": [],
        "decision_style": "UNKNOWN",
        "risk_profile": "UNKNOWN",
        "routine_patterns": [],
        "memory_summary": "",
        "confidence": {},
        "updated_at": _now(),
        "version": VERSION,
    }

def build_digital_twin_snapshot(sender: str, ctx: Dict[str, Any] | None = None, path: Path = STORE_PATH) -> Dict[str, Any]:
    sender = str(sender or "unknown").strip() or "unknown"
    ctx = dict(ctx or {})
    store = _load(path)
    profile = store.get(sender) or _profile(sender)

    rel = ctx.get("p19p36o_relationship_memory_shadow", {}).get("profile", {}) or {}
    goals = rel.get("goals", []) or []
    projects = rel.get("projects", []) or []
    prefs = rel.get("preferences", []) or []
    facts = rel.get("facts", []) or []

    for g in goals:
        if g not in profile["goals"]:
            profile["goals"].append(g)
    for p in projects:
        if p not in profile["projects"]:
            profile["projects"].append(p)
    for p in prefs:
        if p not in profile["preferences"]:
            profile["preferences"].append(p)

    for f in facts:
        lf = str(f).lower()
        if any(x in lf for x in ["dor", "joelho", "ombro", "tempo", "cansaço"]):
            if f not in profile["constraints"]:
                profile["constraints"].append(f)

    goal_shadow = ctx.get("p19p36p_long_term_goal_shadow", {}) or {}
    goal_count = len(goal_shadow.get("goals", []) or [])
    profile["confidence"]["goals"] = "MEDIUM" if goal_count else profile["confidence"].get("goals", "LOW")

    profile["memory_summary"] = "; ".join(profile["goals"][:5] + profile["projects"][:5] + profile["constraints"][:5])
    profile["updated_at"] = _now()
    store[sender] = profile
    _save(store, path)

    return {
        "enabled": enabled(),
        "sender": sender,
        "profile": profile,
        "mode": "SHADOW_ONLY",
        "version": VERSION,
    }

def attach_digital_twin_shadow(ctx: Dict[str, Any] | None = None, sender: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p37a_digital_twin_real_shadow"] = build_digital_twin_snapshot(sender, ctx)
    return ctx


def build_p19p43_digital_twin_evolution(
    *,
    user_profile=None,
    interests=None,
    goals=None,
    relationship_memory=None,
    behavior_model=None,
):
    """
    P19P43 Digital Twin Evolution.

    Shadow-only evolution layer.
    Does not mutate runtime.
    Does not mutate outbound responses.
    """

    profile = dict(user_profile or {})
    interest_items = list(interests or [])
    goal_items = list(goals or [])
    relationship = dict(relationship_memory or {})
    behavior = dict(behavior_model or {})

    signals = {
        "profile_signal_count": len(profile.keys()),
        "interest_signal_count": len(interest_items),
        "goal_signal_count": len(goal_items),
        "relationship_signal_count": len(relationship.keys()),
        "behavior_signal_count": len(behavior.keys()),
    }

    total = sum(signals.values())
    confidence = min(1.0, round(total / 10.0, 4))

    return {
        "program": "P19P43",
        "mode": "SHADOW_ONLY",
        "digital_twin_evolution": {
            "user_profile_evolution": profile,
            "interest_evolution": interest_items,
            "goal_evolution": goal_items,
            "relationship_evolution": relationship,
            "behavior_evidence": behavior,
            "confidence_scoring": {
                "score": confidence,
                "basis": signals,
            },
        },
        "safety": {
            "runtime_mutation": False,
            "response_mutation": False,
            "rollbackable": True,
            "canary_ready": True,
        },
    }

