import json
from pathlib import Path

def test_p483_safe_code_generation_gate_contract():
    gate = json.loads(Path("runtime/governance/safe_code_generation_gate.json").read_text(encoding="utf-8"))
    lock = json.loads(Path("runtime/execution_locks/auto_execution_lock.json").read_text(encoding="utf-8"))
    contract = json.loads(Path("runtime/approval_contracts/mission_approval_contract.json").read_text(encoding="utf-8"))

    assert gate["milestone"] == "P4.83 COMPLETE"
    assert gate["automatic_implementation"] == "FORBIDDEN"
    assert gate["automatic_file_mutation"] == "FORBIDDEN"
    assert gate["approval_required"] is True
    assert gate["default_state"] == "REVIEW"
    assert gate["states"] == ["REVIEW", "APPROVAL", "EXECUTION"]

    assert lock["status"] == "LOCKED"
    assert lock["real_execution"] == "FORBIDDEN"
    assert lock["code_generation_execution"] == "FORBIDDEN"

    assert contract["approval_status"] == "PENDING_REVIEW"
    assert contract["rollback_required"] is True
    assert contract["evidence_required"] is True
