import json
from pathlib import Path

def test_p489b2_routing_safety_audit():
    audit = json.loads(Path("runtime/file_ingestion/routing_safety/routing_safety_audit.json").read_text(encoding="utf-8"))
    allow = json.loads(Path("runtime/file_ingestion/routing_safety/approved_move_allowlist.json").read_text(encoding="utf-8"))
    deny = json.loads(Path("runtime/file_ingestion/routing_safety/protected_denylist.json").read_text(encoding="utf-8"))

    assert audit["milestone"] == "P4.89B2 COMPLETE"
    assert audit["mode"] == "SAFETY_AUDIT_ONLY"
    assert audit["physical_move"] == "FORBIDDEN"
    assert audit["physical_delete"] == "FORBIDDEN"
    assert audit["governance"] == "P4.83_ENFORCED"

    assert audit["total_routes"] == allow["count"] + deny["count"]
    assert deny["count"] >= 1

    for item in deny["items"][:100]:
        assert item["routing_decision"] in ["DENY_MOVE_ACTIVE_REPO_FILE", "DENY_UNCLEAR_RISK"]
