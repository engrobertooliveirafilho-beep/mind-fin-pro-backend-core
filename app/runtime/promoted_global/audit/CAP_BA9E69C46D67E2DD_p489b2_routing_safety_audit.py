import json
from pathlib import Path
from datetime import datetime, timezone

PLAN = Path("runtime/file_ingestion/routing/physical_routing_plan.json")
OUT = Path("runtime/file_ingestion/routing_safety/routing_safety_audit.json")
ALLOW = Path("runtime/file_ingestion/routing_safety/approved_move_allowlist.json")
DENY = Path("runtime/file_ingestion/routing_safety/protected_denylist.json")

plan = json.loads(PLAN.read_text(encoding="utf-8"))
routes = plan.get("routes", [])

PROTECTED_PREFIXES = [
    "app/",
    "tests/",
    "tools/",
    "runtime/",
]

MOVABLE_PREFIXES = [
    "_evidence/",
    "_backup/",
    "backups/",
    "evidence/",
    "_maintenance/",
]

TRASH_HINTS = [
    "__pycache__",
    ".pytest_cache",
    ".cache",
    ".tmp",
    ".bak",
    ".log",
    "Thumbs.db",
    ".DS_Store",
]

allow = []
deny = []

def norm(p):
    return str(p or "").replace("\\", "/")

for r in routes:
    src = norm(r.get("source"))
    q = r.get("queue")

    is_protected = any(src.startswith(x) for x in PROTECTED_PREFIXES)
    is_movable_root = any(src.startswith(x) for x in MOVABLE_PREFIXES)
    is_trash = any(x.lower() in src.lower() for x in TRASH_HINTS)

    decision = {
        **r,
        "safety_audit": {
            "protected_active_code": is_protected,
            "movable_root": is_movable_root,
            "trash_candidate": is_trash,
        }
    }

    if is_protected:
        decision["routing_decision"] = "DENY_MOVE_ACTIVE_REPO_FILE"
        decision["reason"] = "Arquivo ativo protegido. Não mover fisicamente."
        deny.append(decision)
    elif is_movable_root or is_trash or q in ["CLEAN_TRASH", "ARCHIVE"]:
        decision["routing_decision"] = "ALLOW_AFTER_APPROVAL"
        decision["reason"] = "Arquivo não crítico ou candidato a limpeza/arquivo."
        allow.append(decision)
    else:
        decision["routing_decision"] = "DENY_UNCLEAR_RISK"
        decision["reason"] = "Risco indefinido. Exige revisão manual."
        deny.append(decision)

audit = {
    "milestone": "P4.89B2 COMPLETE",
    "audit": "ROUTING_SAFETY_AUDIT",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "mode": "SAFETY_AUDIT_ONLY",
    "physical_move": "FORBIDDEN",
    "physical_delete": "FORBIDDEN",
    "governance": "P4.83_ENFORCED",
    "total_routes": len(routes),
    "allow_after_approval": len(allow),
    "deny_move": len(deny),
    "protected_prefixes": PROTECTED_PREFIXES,
    "movable_prefixes": MOVABLE_PREFIXES,
    "trash_hints": TRASH_HINTS,
    "next": "P4.89C APPROVED LIMITED ROUTING EXECUTION"
}

OUT.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
ALLOW.write_text(json.dumps({"items": allow, "count": len(allow)}, indent=2, ensure_ascii=False), encoding="utf-8")
DENY.write_text(json.dumps({"items": deny, "count": len(deny)}, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.89B2 COMPLETE",
    "total_routes": len(routes),
    "allow_after_approval": len(allow),
    "deny_move": len(deny),
    "physical_move": "FORBIDDEN",
    "next": "P4.89C APPROVED LIMITED ROUTING EXECUTION"
}, indent=2, ensure_ascii=False))
