import os
import pytest

from app.runtime.p2131_2150_ftmo_paper_compliance_assurance import (
    LOCKS, assert_locks, run_p2131_2150,
)


def test_ftmo_rejects_unsafe_environment_without_overwriting(monkeypatch):
    monkeypatch.setenv("REAL_ORDERS", "ALLOWED")
    with pytest.raises(RuntimeError, match="LOCK_BREACH"):
        assert_locks()
    assert os.environ["REAL_ORDERS"] == "ALLOWED"


def test_ftmo_missing_dependencies_cannot_certify(tmp_path, monkeypatch):
    for key, value in LOCKS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.chdir(tmp_path)
    result = run_p2131_2150(str(tmp_path / "evidence"))
    assert result["status"] == "FAIL"
    assert result["readiness"] == "NOT_CERTIFIED"
    assert result["mission_status"]["P2140_FTMO_PAPER_COMPLIANCE_CERTIFICATION"] == "FAIL"
    assert result["mission_status"]["P2150_OPERATIONAL_READINESS_CERTIFICATION"] == "FAIL"
    assert len(result["missing_dependencies"]) == 6


def test_ftmo_declarations_do_not_prove_guards(tmp_path, monkeypatch):
    import json
    for key, value in LOCKS.items():
        monkeypatch.setenv(key, value)
    monkeypatch.chdir(tmp_path)
    deps = {
        "P2071_2080": "REALTIME_PAPER_RUNTIME_CERTIFIED",
        "P2081_2090": "REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
        "P2091_2100": "REALTIME_INTELLIGENCE_LAYER_CERTIFIED",
        "P2101_2110": "AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED",
        "P2111_2120": "MAXIMUM_TECHNICAL_CAPACITY_CERTIFIED",
        "P2121_PLUS": "CONTINUOUS_MAX_CAPACITY_CERTIFIED",
    }
    for folder, readiness in deps.items():
        path = tmp_path / f"data/runtime/{folder}/evidence/{folder}_FINAL_CERTIFICATION.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"status": "PASS", "readiness": readiness}))
    result = run_p2131_2150(str(tmp_path / "output"))
    assert not result["missing_dependencies"]
    assert result["status"] == "FAIL"
    assert result["mission_status"]["P2132_DAILY_LOSS_GUARD_DECLARATION"] == "FAIL"
    assert result["mission_status"]["P2138_RUNTIME_RISK_KILL_SWITCH_AUDIT"] == "FAIL"
