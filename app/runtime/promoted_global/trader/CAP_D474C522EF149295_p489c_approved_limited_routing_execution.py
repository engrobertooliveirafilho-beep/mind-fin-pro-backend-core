import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

ALLOW = Path("runtime/file_ingestion/routing_safety/approved_move_allowlist.json")
OUT = Path("runtime/file_ingestion/executed_routing/p489c_execution_ledger.json")
ROLLBACK = Path("runtime/file_ingestion/executed_routing/p489c_rollback_manifest.json")

data = json.loads(ALLOW.read_text(encoding="utf-8"))
items = data.get("items", [])

EXEC_ALLOWED_QUEUES = {"ARCHIVE", "CLEAN_TRASH"}
PROTECTED_PREFIXES = ("app/", "tests/", "tools/", "runtime/")

executed = []
skipped = []

for item in items:
    src = str(item.get("source", "")).replace("\\", "/")
    queue = item.get("queue")

    if queue not in EXEC_ALLOWED_QUEUES:
        skipped.append({**item, "skip_reason": "QUEUE_NOT_ALLOWED_IN_P4.89C"})
        continue

    if src.startswith(PROTECTED_PREFIXES):
        skipped.append({**item, "skip_reason": "PROTECTED_PREFIX"})
        continue

    source = Path(src)
    if not source.exists():
        skipped.append({**item, "skip_reason": "SOURCE_NOT_FOUND"})
        continue

    safe_name = src.replace("/", "__").replace("\\", "__").replace(":", "_")
    target_root = Path("runtime/file_ingestion/executed_routing/clean_trash" if queue == "CLEAN_TRASH" else "runtime/file_ingestion/executed_routing/archive")
    target = target_root / safe_name
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        skipped.append({**item, "skip_reason": "TARGET_ALREADY_EXISTS", "target": str(target.as_posix())})
        continue

    shutil.move(str(source), str(target))

    executed.append({
        "source": src,
        "target": str(target.as_posix()),
        "queue": queue,
        "moved": True,
        "delete": False,
        "rollback": {
            "from": str(target.as_posix()),
            "to": src
        }
    })

ledger = {
    "milestone": "P4.89C COMPLETE",
    "execution": "APPROVED_LIMITED_ROUTING_EXECUTION",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "approval_source": "user_explicit_prossiga_after_P4.89B2",
    "mode": "LIMITED_PHYSICAL_MOVE",
    "delete": "FORBIDDEN",
    "allowed_queues": sorted(EXEC_ALLOWED_QUEUES),
    "protected_prefixes": list(PROTECTED_PREFIXES),
    "executed_count": len(executed),
    "skipped_count": len(skipped),
    "executed": executed,
    "skipped": skipped,
    "next": "P4.89D POST_ROUTING_VALIDATION_AND_KG_REFRESH"
}

rollback = {
    "milestone": "P4.89C COMPLETE",
    "rollback_available": True,
    "items_count": len(executed),
    "items": [x["rollback"] for x in executed]
}

OUT.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")
ROLLBACK.write_text(json.dumps(rollback, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89C COMPLETE",
    "executed": len(executed),
    "skipped": len(skipped),
    "delete": "FORBIDDEN",
    "next": "P4.89D POST_ROUTING_VALIDATION_AND_KG_REFRESH"
}, indent=2, ensure_ascii=False))
