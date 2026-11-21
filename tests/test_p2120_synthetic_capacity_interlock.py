from app.runtime.p2111_2120_maximum_technical_capacity import (
    CapacityDecision, CapabilityGapAudit, certify
)

def _decision(step, status="PASS"):
    return CapacityDecision(component=f"P{step}_TEST", status=status, reason="TEST", payload={})

def test_gap_audit_rejects_missing_dependencies():
    d = CapabilityGapAudit().evaluate({})
    assert d.status == "FAIL"
    assert set(d.payload["gaps"]) == {"p2071", "p2081", "p2091", "p2101"}

def test_gap_audit_rejects_failed_upstream():
    deps = {k: {"status": "PASS"} for k in ("p2071", "p2081", "p2091", "p2101")}
    deps["p2071"]["status"] = "FAIL"
    assert CapabilityGapAudit().evaluate(deps).status == "FAIL"

def test_p2120_rejects_empty_steps():
    assert certify([]).status == "FAIL"

def test_p2120_rejects_duplicate_steps():
    decisions = [_decision(i) for i in range(2111, 2120)]
    decisions[8] = _decision(2118)
    assert certify(decisions).status == "FAIL"

def test_p2120_blocks_synthetic_only_maximum_capacity_claim():
    decisions = [_decision(i) for i in range(2111, 2120)]
    d = certify(decisions)
    assert d.status == "FAIL"
    assert d.reason == "MAXIMUM_CAPACITY_NOT_CERTIFIED"

def test_p2120_failure_never_reports_certified_capability_flags(tmp_path, monkeypatch):
    import json
    from pathlib import Path
    from app.runtime.p2111_2120_maximum_technical_capacity import run_p2111_2120
    repo = tmp_path / "repo"
    (repo / "app" / "runtime").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "app" / "runtime" / "probe.py").write_text("x=1")
    (repo / "tests" / "test_probe.py").write_text("def test_probe(): assert True")
    for name in ("p2071", "p2081", "p2091", "p2101", "portfolio"):
        (tmp_path / (name + ".json")).write_text(json.dumps({"status": "FAIL"}))
    result = run_p2111_2120(
        str(repo), str(tmp_path / "portfolio.json"),
        *(str(tmp_path / (name + ".json")) for name in ("p2071", "p2081", "p2091", "p2101")),
        str(tmp_path / "out"),
    )
    assert result["status"] == "FAIL"
    assert result["readiness"] == "NOT_CERTIFIED"
    for flag in ("runtime_resilient", "runtime_autonomous", "runtime_observable",
                 "runtime_auditable", "runtime_recoverable", "runtime_scalable",
                 "runtime_governable"):
        assert result["final_state"][flag] is False
