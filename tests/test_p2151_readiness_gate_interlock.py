import json
import os
import pytest

from app.runtime.p2151_plus_readiness_dossier_gate_review import LOCKS, run_p2151_plus


def test_p2151_unsafe_environment_is_rejected_before_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("REAL_ORDERS", "ALLOWED")
    output = tmp_path / "must_not_exist"
    with pytest.raises(RuntimeError, match="REAL_ORDERS_LOCK_BREACH"):
        run_p2151_plus(str(output))
    assert os.environ["REAL_ORDERS"] == "ALLOWED"
    assert not output.exists()


def test_p2151_missing_dependencies_blocks_deployment(tmp_path, monkeypatch):
    for k, v in LOCKS.items():
        monkeypatch.setenv(k, v)
    monkeypatch.chdir(tmp_path)
    result = run_p2151_plus(str(tmp_path / "out"))
    assert result["status"] == "FAIL"
    assert result["readiness"] == "NOT_READY"
    assert result["gate_review"]["deployment_decision"] == "BLOCKED"
    assert result["executive_conclusion"]["technical_capacity"] == "NOT_CERTIFIED"
    assert len(result["missing"]) == 7


def test_p2151_historical_pass_is_not_e2e_authority(tmp_path, monkeypatch):
    for k, v in LOCKS.items():
        monkeypatch.setenv(k, v)
    monkeypatch.chdir(tmp_path)
    paths = {
        "P2071_2080": "REALTIME_PAPER_RUNTIME_CERTIFIED",
        "P2081_2090": "REALTIME_PORTFOLIO_GOVERNANCE_CERTIFIED",
        "P2091_2100": "REALTIME_INTELLIGENCE_LAYER_CERTIFIED",
        "P2101_2110": "AUTONOMOUS_PAPER_OPERATIONS_CERTIFIED",
        "P2111_2120": "MAXIMUM_TECHNICAL_CAPACITY_CERTIFIED",
        "P2121_PLUS": "CONTINUOUS_MAX_CAPACITY_CERTIFIED",
        "P2131_2150": "FTMO_PAPER_COMPLIANCE_AND_OPERATIONAL_ASSURANCE_CERTIFIED",
    }
    for block, readiness in paths.items():
        path = tmp_path / f"data/runtime/{block}/evidence/{block}_FINAL_CERTIFICATION.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"status": "PASS", "readiness": readiness}))
    result = run_p2151_plus(str(tmp_path / "out"))
    assert not result["missing"]
    assert not result["failed"]
    assert result["status"] == "FAIL"
    assert result["gate_review"]["deployment_decision"] == "BLOCKED"

@pytest.mark.parametrize("payload,code", [
    ('{"status":"PASS","status":"FAIL"}', "P2151_DUPLICATE_JSON_KEY"),
    ('{"x":NaN}', "P2151_NONFINITE_JSON_NUMBER"),
    ('{"x":Infinity}', "P2151_NONFINITE_JSON_NUMBER"),
    ('{"x":1e999}', "P2151_NONFINITE_JSON_NUMBER"),
    ('["PASS"]', "P2151_INVALID_CERTIFICATION_OBJECT"),
])
def test_p2151_rejects_ambiguous_certification(tmp_path, payload, code):
    from app.runtime.p2151_plus_readiness_dossier_gate_review import load
    path=tmp_path/"cert.json"
    path.write_text(payload,encoding="utf-8")
    with pytest.raises(ValueError,match=code):
        load(str(path))
