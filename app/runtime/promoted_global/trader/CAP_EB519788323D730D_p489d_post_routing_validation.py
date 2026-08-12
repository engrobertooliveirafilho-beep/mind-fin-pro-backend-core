import json
from pathlib import Path
from datetime import datetime, timezone

LEDGER = Path("runtime/file_ingestion/executed_routing/p489c_execution_ledger.json")
ROLLBACK = Path("runtime/file_ingestion/executed_routing/p489c_rollback_manifest.json")
KG = Path("runtime/knowledge_graph/drive_knowledge_graph.json")
OUT = Path("runtime/file_ingestion/validation/post_routing_validation_report.json")

ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
rollback = json.loads(ROLLBACK.read_text(encoding="utf-8"))
kg = json.loads(KG.read_text(encoding="utf-8")) if KG.exists() else {}

executed = ledger.get("executed", [])
skipped = ledger.get("skipped", [])
errors = ledger.get("errors", [])

valid_moves = []
missing_targets = []

for item in executed:
    target = Path(item["target"])
    if target.exists():
        valid_moves.append(item)
    else:
        missing_targets.append(item)

kg_refresh = {
    "previous_nodes": kg.get("nodes_count", 0),
    "previous_edges": kg.get("edges_count", 0),
    "routing_nodes_added": len(valid_moves),
    "routing_edges_added": len(valid_moves),
    "refresh_mode": "STATE_REFRESH_ONLY"
}

validation = {
    "milestone": "P4.89D COMPLETE",
    "validation": "POST_ROUTING_VALIDATION_AND_KG_REFRESH",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "VALIDATION_ONLY",
    "physical_move": "NOT_EXECUTED_IN_THIS_STAGE",
    "delete": "FORBIDDEN",
    "executed_count": len(executed),
    "valid_targets": len(valid_moves),
    "missing_targets": len(missing_targets),
    "skipped_count": len(skipped),
    "errors_count": len(errors),
    "rollback_available": rollback.get("rollback_available") is True,
    "rollback_items": rollback.get("items_count", 0),
    "kg_refresh": kg_refresh,
    "ready_for_p490": len(missing_targets) == 0 and len(errors) == 0 and rollback.get("rollback_available") is True,
    "next": "P4.90 SOVEREIGN TECHNICAL CAPACITY CERTIFICATION"
}

OUT.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89D COMPLETE",
    "executed": len(executed),
    "valid_targets": len(valid_moves),
    "missing_targets": len(missing_targets),
    "errors": len(errors),
    "rollback_available": validation["rollback_available"],
    "ready_for_p490": validation["ready_for_p490"],
    "next": validation["next"]
}, indent=2, ensure_ascii=False))
