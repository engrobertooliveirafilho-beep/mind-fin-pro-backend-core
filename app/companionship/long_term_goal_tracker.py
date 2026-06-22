import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


STORE_PATH = Path("_runtime_state/p19p36p_long_term_goals.json")
TELEMETRY_PATH = Path("_runtime_state/p19p36p_long_term_goal_telemetry.jsonl")
VERSION = "P19P36P_A_LONG_TERM_GOAL_TRACKING_FOUNDATION"


def goal_tracking_enabled() -> bool:
    return str(os.getenv("P19P36P_GOAL_TRACKING_ENABLED", "false")).lower() in {
        "1", "true", "yes", "on"
    }


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _goal_id(sender: str, goal_name: str) -> str:
    raw = f"{sender}|{goal_name}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


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


def _telemetry(sender: str, goal_id: str, goal_name: str, action: str) -> None:
    try:
        TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        event = {
            "timestamp": _now(),
            "sender": sender,
            "goal_id": goal_id,
            "goal_name": goal_name,
            "action": action,
            "version": VERSION,
        }
        with TELEMETRY_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _empty_goal(sender: str, goal_name: str) -> Dict[str, Any]:
    gid = _goal_id(sender, goal_name)
    now = _now()
    return {
        "goal_id": gid,
        "sender": sender,
        "goal_name": goal_name,
        "status": "ACTIVE_SHADOW",
        "first_seen": now,
        "last_seen": now,
        "progress_events": [],
        "constraints": [],
        "next_actions": [],
        "confidence": "LOW_RULE_BASED",
        "version": VERSION,
    }


def extract_goal_signals_from_relationship_profile(profile: Dict[str, Any]) -> List[str]:
    goals = profile.get("goals", []) if isinstance(profile, dict) else []
    out = []
    for g in goals:
        val = str(g or "").strip()
        if val and val not in out:
            out.append(val)
    return out


def update_goal_tracker_from_relationship_profile(
    sender: str,
    profile: Dict[str, Any],
    text: str = "",
    path: Path = STORE_PATH,
) -> Dict[str, Any]:
    sender = str(sender or "unknown").strip() or "unknown"
    store = _load(path)
    sender_goals = store.get(sender) or {}

    goal_names = extract_goal_signals_from_relationship_profile(profile)
    changed = False

    for goal_name in goal_names:
        gid = _goal_id(sender, goal_name)

        if gid not in sender_goals:
            sender_goals[gid] = _empty_goal(sender, goal_name)
            changed = True
            _telemetry(sender, gid, goal_name, "created")
        else:
            sender_goals[gid]["last_seen"] = _now()
            _telemetry(sender, gid, goal_name, "seen")

        if text:
            event = {
                "timestamp": _now(),
                "text_preview": str(text)[:240],
                "type": "MENTION",
            }
            if event not in sender_goals[gid]["progress_events"]:
                sender_goals[gid]["progress_events"].append(event)
                changed = True

    store[sender] = sender_goals
    _save(store, path)

    return {
        "enabled": goal_tracking_enabled(),
        "changed": changed,
        "sender": sender,
        "goals": list(sender_goals.values()),
        "mode": "SHADOW_ONLY",
        "version": VERSION,
    }


def get_goals_for_sender(sender: str, path: Path = STORE_PATH) -> List[Dict[str, Any]]:
    sender = str(sender or "unknown").strip() or "unknown"
    store = _load(path)
    return list((store.get(sender) or {}).values())
