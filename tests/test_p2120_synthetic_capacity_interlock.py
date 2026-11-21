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

def test_gap_audit_rejects_bare_pass_without_certification_proof():
    deps = {key: {"status": "PASS"} for key in ("p2071", "p2081", "p2091", "p2101")}
    decision = CapabilityGapAudit().evaluate(deps)
    assert decision.status == "FAIL"
    assert set(decision.payload["gaps"]) == set(deps)


def test_gap_audit_rejects_simulation_only_p2080():
    deps = {
        "p2071": {"status": "PASS",
                  "readiness": "SIMULATED_PAPER_RUNTIME_VALIDATED_REALTIME_FEED_NOT_CERTIFIED",
                  "mission_status": {"P2080_REALTIME_RUNTIME_CERTIFICATION": "PASS_SIMULATION_SCOPE_ONLY"}},
        "p2081": {"status": "PASS", "readiness": "REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED"},
        "p2091": {"status": "PASS", "readiness": "REALTIME_INTELLIGENCE_LAYER_CERTIFIED"},
        "p2101": {"status": "PASS", "readiness": "AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED"},
    }
    decision = CapabilityGapAudit().evaluate(deps)
    assert decision.status == "FAIL"
    assert decision.payload["gaps"] == ["p2071"]

def test_p2111_inventory_is_not_functional_certification(tmp_path):
    from app.runtime.p2111_2120_maximum_technical_capacity import CapabilityDiscovery
    root = tmp_path / "repo"
    (root / "app" / "runtime").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "app" / "runtime" / "runtime.py").write_text("x = 1")
    (root / "tests" / "test_runtime.py").write_text("def test_x(): assert True")
    result = CapabilityDiscovery().evaluate(str(root))
    assert result.payload["python_files"] == 2
    assert result.payload["tests"] == 1
    assert result.payload["runtime_modules"] == 1
    assert result.status == "FAIL"
    assert result.reason == "CAPABILITY_DISCOVERY_INCOMPLETE"

def test_p2113_rejects_empty_and_syntax_invalid_modules(tmp_path):
    from app.runtime.p2111_2120_maximum_technical_capacity import MissingComponentsAudit
    expected = [
        "p2071_2080_realtime_paper_runtime.py",
        "p2081_2090_realtime_portfolio_governance.py",
        "p2091_2100_realtime_intelligence_layer.py",
        "p2101_2110_autonomous_paper_operations.py",
    ]
    runtime = tmp_path / "app" / "runtime"
    runtime.mkdir(parents=True)
    (runtime / expected[0]).write_text("", encoding="utf-8")
    (runtime / expected[1]).write_text("def broken(:", encoding="utf-8")
    (runtime / expected[2]).write_text("def available(): return 1", encoding="utf-8")
    decision = MissingComponentsAudit().evaluate(str(tmp_path))
    assert decision.status == "FAIL"
    assert decision.payload["syntax_checked"] == 1
    assert len(decision.payload["invalid"]) == 2
    assert len(decision.payload["missing"]) == 1


def test_p2113_does_not_certify_even_syntax_valid_modules(tmp_path):
    from app.runtime.p2111_2120_maximum_technical_capacity import MissingComponentsAudit
    runtime = tmp_path / "app" / "runtime"
    runtime.mkdir(parents=True)
    for name in (
        "p2071_2080_realtime_paper_runtime.py",
        "p2081_2090_realtime_portfolio_governance.py",
        "p2091_2100_realtime_intelligence_layer.py",
        "p2101_2110_autonomous_paper_operations.py",
    ):
        (runtime / name).write_text("def stub(): return None", encoding="utf-8")
    decision = MissingComponentsAudit().evaluate(str(tmp_path))
    assert decision.payload["syntax_checked"] == 4
    assert decision.payload["missing"] == []
    assert decision.payload["invalid"] == []
    assert decision.status == "FAIL"
