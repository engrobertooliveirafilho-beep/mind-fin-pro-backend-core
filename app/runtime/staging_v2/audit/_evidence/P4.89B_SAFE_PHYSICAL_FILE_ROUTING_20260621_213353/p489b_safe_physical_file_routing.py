import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("runtime/file_ingestion")
LEDGER = BASE / "processing_ledger.json"
OUT = BASE / "routing"

files = json.loads(LEDGER.read_text(encoding="utf-8"))

DEST = {
    "PROCESS": "runtime/file_ingestion/routing/planned_processed",
    "REVIEW": "runtime/file_ingestion/routing/planned_review",
    "ARCHIVE": "runtime/file_ingestion/routing/planned_archive",
    "CLEAN_TRASH": "runtime/file_ingestion/routing/planned_clean_trash",
}

routes = []

for item in files:
    q = item.get("queue", "ARCHIVE")
    target_root = DEST.get(q, DEST["ARCHIVE"])
    original = item["path"]
    safe_name = original.replace("/", "__").replace("\\", "__").replace(":", "_")
    planned_target = f"{target_root}/{safe_name}"

    routes.append({
        "source": original,
        "queue": q,
        "planned_target": planned_target,
        "physical_move_status": "NOT_EXECUTED",
        "execution_blocked_by": "P4.83_GATE",
        "approval_required": True,
        "rollback": {
            "source": planned_target,
            "restore_to": original,
            "required": True
        }
    })

routing_plan = {
    "milestone": "P4.89B COMPLETE",
    "pipeline": "SAFE_PHYSICAL_FILE_ROUTING",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "PLAN_ONLY",
    "physical_move": "FORBIDDEN_WITHOUT_APPROVAL",
    "physical_delete": "FORBIDDEN",
    "governance": "P4.83_ENFORCED",
    "total_routes": len(routes),
    "destinations": DEST,
    "routes": routes,
    "next": "P4.89C APPROVED FILE ROUTING EXECUTION"
}

rollback_manifest = {
    "milestone": "P4.89B COMPLETE",
    "rollback_manifest": "SAFE_FILE_ROUTING_ROLLBACK",
    "mode": "PLAN_ONLY",
    "total_items": len(routes),
    "items": [r["rollback"] for r in routes],
    "rollback_execution": "FORBIDDEN_WITHOUT_APPROVAL"
}

(OUT / "physical_routing_plan.json").write_text(json.dumps(routing_plan, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "rollback_manifest.json").write_text(json.dumps(rollback_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89B COMPLETE",
    "routes": len(routes),
    "mode": "PLAN_ONLY",
    "physical_move": "FORBIDDEN_WITHOUT_APPROVAL",
    "physical_delete": "FORBIDDEN",
    "next": "P4.89C APPROVED FILE ROUTING EXECUTION"
}, indent=2, ensure_ascii=False))
