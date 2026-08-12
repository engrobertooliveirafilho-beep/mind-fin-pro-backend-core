import json
from pathlib import Path

def test_p489b_safe_physical_file_routing_plan_only():
    plan = json.loads(Path("runtime/file_ingestion/routing/physical_routing_plan.json").read_text(encoding="utf-8"))
    rollback = json.loads(Path("runtime/file_ingestion/routing/rollback_manifest.json").read_text(encoding="utf-8"))

    assert plan["milestone"] == "P4.89B COMPLETE"
    assert plan["mode"] == "PLAN_ONLY"
    assert plan["physical_move"] == "FORBIDDEN_WITHOUT_APPROVAL"
    assert plan["physical_delete"] == "FORBIDDEN"
    assert plan["governance"] == "P4.83_ENFORCED"
    assert plan["total_routes"] >= 1

    assert rollback["milestone"] == "P4.89B COMPLETE"
    assert rollback["rollback_execution"] == "FORBIDDEN_WITHOUT_APPROVAL"
    assert rollback["total_items"] == plan["total_routes"]

    for route in plan["routes"][:50]:
        assert route["physical_move_status"] == "NOT_EXECUTED"
        assert route["execution_blocked_by"] == "P4.83_GATE"
        assert route["approval_required"] is True
        assert route["rollback"]["required"] is True
