import pytest

from app.runtime.p2121_plus_continuous_max_capacity_audit import (
    ABSOLUTE_LOCKS, CertifiedBlockAudit, assert_no_financial_execution,
)


def test_p2121_rejects_unsafe_live_environment(monkeypatch):
    monkeypatch.setenv("REAL_ORDERS", "ALLOWED")
    with pytest.raises(RuntimeError, match="REAL_ORDERS_LOCK_BREACH"):
        assert_no_financial_execution()
    assert __import__("os").environ["REAL_ORDERS"] == "ALLOWED"


def test_p2121_rejects_upstream_pass_without_proven_readiness(tmp_path, monkeypatch):
    import json
    for key, expected in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(key, expected)
    deps = {}
    for key in ("p2071", "p2081", "p2091", "p2101", "p2111"):
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps({"status": "PASS", "readiness": "NOT_CERTIFIED"}))
        deps[key] = str(path)
    decision = CertifiedBlockAudit().evaluate(deps)
    assert decision.status == "FAIL"
    assert set(decision.payload["failures"]) == set(deps)


def test_p2121_p2111_cannot_be_promoted_by_unverified_pass(tmp_path, monkeypatch):
    import json
    for key, expected in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(key, expected)
    readiness = {
        "p2071": "REALTIME_PAPER_RUNTIME_CERTIFIED",
        "p2081": "REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
        "p2091": "REALTIME_INTELLIGENCE_LAYER_CERTIFIED",
        "p2101": "AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED",
        "p2111": "MAXIMUM_TECHNICAL_CAPACITY_CERTIFIED",
    }
    deps = {}
    for key, state in readiness.items():
        path = tmp_path / f"{key}.json"
        path.write_text(json.dumps({"status": "PASS", "readiness": state}))
        deps[key] = str(path)
    decision = CertifiedBlockAudit().evaluate(deps)
    assert decision.status == "FAIL"
    assert decision.payload["failures"] == ["p2111"]
