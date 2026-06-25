import json
from pathlib import Path
from datetime import datetime, timezone

PLAN_DIR = Path("runtime/reconstruction_plans")
PLAN_DIR.mkdir(parents=True, exist_ok=True)

def _slug(text: str) -> str:
    keep = []
    for ch in (text or "").lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in [" ", "-", "_"]:
            keep.append("_")
    return "".join(keep)[:80].strip("_") or "item"

def plan_from_extraction(extraction: dict) -> dict:
    items = extraction.get("items", [])

    missions = []

    for idx, item in enumerate(items, start=1):
        t = item.get("type")
        priority = item.get("priority", "MEDIUM")
        text = item.get("text", "")

        if t in ["UNIMPLEMENTED_IDEA", "INCOMPLETE_FEATURE", "BUG_FIX", "CAPABILITY", "ARCHITECTURE"]:
            title = text[:90].replace("\n", " ")

            mission = {
                "mission_id": f"P4.80_AUTO_{idx:03d}",
                "source_id": item.get("source_id"),
                "type": t,
                "priority": priority,
                "title": title,
                "evidence_text": text,
                "recommended_action": "REVIEW",
                "suggested_files": [],
                "suggested_tests": [],
                "risk": "medium"
            }

            if t == "BUG_FIX":
                mission["recommended_action"] = "CREATE_FIX_TASK"
                mission["risk"] = "high"
                mission["suggested_tests"].append("tests/test_regression_from_extraction.py")

            elif t == "UNIMPLEMENTED_IDEA":
                mission["recommended_action"] = "CREATE_IMPLEMENTATION_PROPOSAL"
                mission["suggested_files"].append("app/runtime/" + _slug(title) + ".py")
                mission["suggested_tests"].append("tests/test_" + _slug(title)[:40] + ".py")

            elif t == "INCOMPLETE_FEATURE":
                mission["recommended_action"] = "CREATE_COMPLETION_TASK"
                mission["risk"] = "high"

            elif t == "CAPABILITY":
                mission["recommended_action"] = "MAP_TO_REGISTRY_OR_CREATE_ADAPTER"

            elif t == "ARCHITECTURE":
                mission["recommended_action"] = "ARCHITECTURE_REVIEW"

            missions.append(mission)

    plan = {
        "engine": "P4.80_CAPABILITY_RECONSTRUCTION_PLANNER",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_id": extraction.get("source_id"),
        "total_missions": len(missions),
        "missions": missions,
        "summary": {}
    }

    for m in missions:
        plan["summary"][m["recommended_action"]] = plan["summary"].get(m["recommended_action"], 0) + 1

    out = PLAN_DIR / f"{str(plan.get('source_id')).replace('/', '_').replace(':', '_')}.json"
    out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    return plan
