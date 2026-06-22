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

# ---------------------------------------------------------------------
# P19P36P-C GOAL PROGRESS ADVISOR
# Shadow-only goal progress analysis.
# ---------------------------------------------------------------------
def _p19p36p_lower(text: str) -> str:
    return str(text or "").lower().strip()


def _p19p36p_detect_constraints(text: str) -> List[str]:
    lower = _p19p36p_lower(text)
    constraints = []

    if "dor" in lower:
        constraints.append("dor")
    if "joelho" in lower:
        constraints.append("joelho")
    if "ombro" in lower:
        constraints.append("ombro")
    if "sem tempo" in lower or "correria" in lower:
        constraints.append("tempo")
    if "cansado" in lower or "cansaço" in lower:
        constraints.append("cansaço")

    return list(dict.fromkeys(constraints))


def _p19p36p_detect_progress_signal(text: str) -> str:
    lower = _p19p36p_lower(text)

    positive_terms = [
        "treinei", "estudei", "fiz", "executei", "consegui", "melhorei",
        "avancei", "completei", "bati", "reduzi", "perdi peso"
    ]

    negative_terms = [
        "parei", "não consegui", "nao consegui", "falhei", "regredi",
        "piorou", "desisti", "travei"
    ]

    if any(t in lower for t in positive_terms):
        return "PROGRESS"
    if any(t in lower for t in negative_terms):
        return "BLOCKED"
    if _p19p36p_detect_constraints(lower):
        return "CONSTRAINT"
    return "MENTION"


def build_goal_progress_advisor(sender: str, text: str, path: Path = STORE_PATH) -> Dict[str, Any]:
    goals = get_goals_for_sender(sender, path=path)
    lower = _p19p36p_lower(text)

    goal_reports = []
    constraints = _p19p36p_detect_constraints(text)
    signal = _p19p36p_detect_progress_signal(text)

    for goal in goals:
        goal_name = str(goal.get("goal_name") or "")
        goal_lower = goal_name.lower()

        related = False
        if goal_lower and goal_lower in lower:
            related = True
        if "exerc" in lower and ("emagrecer" in goal_lower or "fitness" in goal_lower):
            related = True
        if "trein" in lower and ("emagrecer" in goal_lower or "fitness" in goal_lower):
            related = True
        if "ftmo" in lower and "ftmo" in goal_lower:
            related = True

        if not related:
            continue

        recent_events = goal.get("progress_events", [])[-5:]

        score = 0.25
        if signal == "PROGRESS":
            score += 0.45
        elif signal == "CONSTRAINT":
            score += 0.15
        elif signal == "BLOCKED":
            score += 0.05

        if recent_events:
            score += min(0.20, len(recent_events) * 0.04)

        score = min(1.0, score)

        next_actions = []
        if "emagrecer" in goal_lower:
            next_actions.append("manter registro simples de treino, dor e alimentação")
            if constraints:
                next_actions.append("adaptar intensidade considerando restrições relatadas")
        if "ftmo" in goal_lower:
            next_actions.append("registrar consistência, risco e regras da avaliação")
        if not next_actions:
            next_actions.append("acompanhar próximo progresso relatado")

        goal_reports.append({
            "goal_id": goal.get("goal_id"),
            "goal_name": goal_name,
            "progress_score": round(score, 4),
            "goal_status_signal": signal,
            "recent_mentions": recent_events,
            "constraints_detected": constraints,
            "next_action_candidates": next_actions,
        })

    overall = 0.0
    if goal_reports:
        overall = round(max(g["progress_score"] for g in goal_reports), 4)

    return {
        "sender": sender,
        "progress_score": overall,
        "goal_reports": goal_reports,
        "constraints_detected": constraints,
        "goal_status_signal": signal if goal_reports else "NO_RELATED_GOAL",
        "mode": "SHADOW_ONLY",
        "version": "P19P36P_C_GOAL_PROGRESS_ADVISOR",
    }


def attach_goal_progress_advisor_shadow(ctx: Dict[str, Any] | None = None, sender: str = "", text: str = "") -> Dict[str, Any]:
    ctx = dict(ctx or {})
    ctx["p19p36p_goal_progress_advisor_shadow"] = build_goal_progress_advisor(sender, text)
    return ctx
# /P19P36P_C_GOAL_PROGRESS_ADVISOR

