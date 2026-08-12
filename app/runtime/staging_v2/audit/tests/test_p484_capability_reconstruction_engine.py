import json
from pathlib import Path

def test_p484_reconstruction_plan_respects_p483_gate():
    plan_path = Path("runtime/reconstruction/capability_reconstruction_plan.json")
    assert plan_path.exists()

    data = json.loads(plan_path.read_text(encoding="utf-8"))

    assert data["milestone"] == "P4.84 COMPLETE"
    assert data["engine"] == "CAPABILITY_RECONSTRUCTION_ENGINE"
    assert data["execution_policy"]["implementation"] == "FORBIDDEN"
    assert data["execution_policy"]["mode"] == "PLAN_ONLY"
    assert data["execution_policy"]["approval_required"] is True

    assert data["total_tasks"] == len(data["tasks"])
    assert data["total_tasks"] >= 1

    for task in data["tasks"]:
        assert task["approval_status"] == "PENDING_APPROVAL"
        assert task["execution_status"] == "BLOCKED_BY_P4.83_GATE"
        assert task["auto_execution_allowed"] is False
        assert task["reconstruction"]["manual_approval_required"] is True
        assert task["reconstruction"]["rollback_required"] is True
        assert task["reconstruction"]["evidence_required"] is True
        assert "target_files" in task["reconstruction"]
        assert "target_tests" in task["reconstruction"]
        assert "dependencies" in task["reconstruction"]
