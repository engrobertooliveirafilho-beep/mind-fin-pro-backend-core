import json
from pathlib import Path
from datetime import datetime, timezone

GOV_DIR = Path("runtime/governance")
LOCK_DIR = Path("runtime/execution_locks")
APPROVAL_DIR = Path("runtime/approval_contracts")

for p in [GOV_DIR, LOCK_DIR, APPROVAL_DIR]:
    p.mkdir(parents=True, exist_ok=True)

gate = {
    "milestone": "P4.83 COMPLETE",
    "gate": "SAFE_CODE_GENERATION_GATE",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "states": ["REVIEW", "APPROVAL", "EXECUTION"],
    "default_state": "REVIEW",
    "automatic_implementation": "FORBIDDEN",
    "automatic_file_mutation": "FORBIDDEN",
    "required_before_execution": [
        "mission_id",
        "risk_score",
        "target_files",
        "test_plan",
        "approval_status"
    ],
    "approval_required": True,
    "execution_allowed_only_if": {
        "approval_status": "APPROVED",
        "execution_lock": "UNLOCKED",
        "target_files_declared": True,
        "tests_declared": True
    }
}

lock = {
    "milestone": "P4.83 COMPLETE",
    "lock_name": "AUTO_EXECUTION_LOCK",
    "status": "LOCKED",
    "reason": "Automatic implementation blocked until explicit approval contract exists.",
    "real_execution": "FORBIDDEN",
    "code_generation_execution": "FORBIDDEN"
}

approval_contract = {
    "milestone": "P4.83 COMPLETE",
    "contract": "MISSION_APPROVAL_CONTRACT",
    "approval_status": "PENDING_REVIEW",
    "approved_by": None,
    "approved_at": None,
    "execution_scope": None,
    "target_files": [],
    "tests_required": [],
    "rollback_required": True,
    "evidence_required": True
}

(GOV_DIR / "safe_code_generation_gate.json").write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
(LOCK_DIR / "auto_execution_lock.json").write_text(json.dumps(lock, indent=2, ensure_ascii=False), encoding="utf-8")
(APPROVAL_DIR / "mission_approval_contract.json").write_text(json.dumps(approval_contract, indent=2, ensure_ascii=False), encoding="utf-8")

print(json.dumps({
    "status": "P4.83 COMPLETE",
    "gate": str(GOV_DIR / "safe_code_generation_gate.json"),
    "lock": str(LOCK_DIR / "auto_execution_lock.json"),
    "approval_contract": str(APPROVAL_DIR / "mission_approval_contract.json"),
    "next": "P4.84 CAPABILITY RECONSTRUCTION ENGINE"
}, indent=2, ensure_ascii=False))
