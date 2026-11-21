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
