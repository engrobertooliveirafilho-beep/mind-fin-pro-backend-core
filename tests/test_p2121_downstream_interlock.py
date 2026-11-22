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

@pytest.mark.parametrize("payload,code", [
    ('{"status":"PASS","status":"FAIL"}', "P2121_DUPLICATE_JSON_KEY"),
    ('{"x":NaN}', "P2121_NONFINITE_JSON_NUMBER"),
    ('{"x":Infinity}', "P2121_NONFINITE_JSON_NUMBER"),
    ('{"x":1e999}', "P2121_NONFINITE_JSON_NUMBER"),
])
def test_p2121_strict_certification_json(tmp_path, payload, code):
    from app.runtime.p2121_plus_continuous_max_capacity_audit import load_json
    path = tmp_path / "evidence.json"
    path.write_text(payload, encoding="utf-8")
    with pytest.raises(ValueError, match=code):
        load_json(str(path))

def test_p2122_rejects_nonempty_tampered_package(tmp_path, monkeypatch):
    from app.runtime.p2121_plus_continuous_max_capacity_audit import PackageIntegrityAudit
    for key, expected in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(key, expected)
    package = tmp_path / "data/runtime/P2071_2080/P2071_2080_PACKAGE_FINAL.zip"
    package.parent.mkdir(parents=True)
    package.write_bytes(b"tampered-not-a-verified-archive")
    decision = PackageIntegrityAudit().evaluate(str(tmp_path))
    assert decision.status == "FAIL"
    assert str(package.relative_to(tmp_path)) in decision.payload["mismatched"]
    assert len(decision.payload["missing"]) == 4

def test_p2121_missing_dependency_does_not_create_artifacts(tmp_path, monkeypatch):
    from app.runtime.p2121_plus_continuous_max_capacity_audit import run_p2121_plus
    for key, expected in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(key, expected)
    deps = {key: str(tmp_path / "absent.json") for key in ("p2071", "p2081", "p2091", "p2101", "p2111")}
    output = tmp_path / "must_not_exist"
    with pytest.raises(FileNotFoundError):
        run_p2121_plus(str(tmp_path), deps, str(output))
    assert not output.exists()
