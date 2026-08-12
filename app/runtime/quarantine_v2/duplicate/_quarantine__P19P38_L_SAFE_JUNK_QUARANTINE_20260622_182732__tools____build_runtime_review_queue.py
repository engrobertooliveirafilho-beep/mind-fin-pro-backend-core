import json
from pathlib import Path
from datetime import datetime, timezone

PLANS_DIR = Path("runtime/reconstruction_plans")
QUEUE_DIR = Path("runtime/review_queue")
QUEUE_FILE = QUEUE_DIR / "runtime_review_queue.json"

QUEUE_DIR.mkdir(parents=True, exist_ok=True)

def build_review_queue():
    items = []

    for p in PLANS_DIR.glob("*.json"):
        try:
            plan = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue

        for mission in plan.get("missions", []):
            items.append({
                "queue_id": f"RQ_{len(items)+1:05d}",
                "source_plan": str(p),
                "mission_id": mission.get("mission_id"),
                "source_id": mission.get("source_id"),
                "type": mission.get("type"),
                "priority": mission.get("priority"),
                "title": mission.get("title"),
                "recommended_action": mission.get("recommended_action"),
                "risk": mission.get("risk"),
                "status": "PENDING_REVIEW",
                "evidence_text": mission.get("evidence_text"),
                "suggested_files": mission.get("suggested_files", []),
                "suggested_tests": mission.get("suggested_tests", []),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

    payload = {
        "engine": "P4.81_RUNTIME_REVIEW_QUEUE",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items),
        "items": items,
        "summary": {}
    }

    for item in items:
        key = item.get("recommended_action") or "UNKNOWN"
        payload["summary"][key] = payload["summary"].get(key, 0) + 1

    QUEUE_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload

if __name__ == "__main__":
    print(json.dumps(build_review_queue(), indent=2, ensure_ascii=False))
