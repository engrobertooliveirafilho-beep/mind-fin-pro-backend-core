import math
import pytest
from app.runtime.p2081_2090_realtime_portfolio_governance import extract_runtime_metrics


def baseline():
    return {"metrics": {
        "cycles": 1000, "frames_built": 1000, "signals_generated": 30,
        "closed_trades": 12, "open_positions": 0, "initial_equity": 100000.,
        "final_mark_to_market_equity": 100500., "paper_mark_to_market_pnl": 500.,
        "drawdown_pct": -0.01, "drawdown_abs": -1000., "max_drawdown_pct": 0.02, "peak_equity": 101000.,
        "trough_equity": 99000.,
    }}


def test_valid_paper_metrics():
    assert extract_runtime_metrics(baseline())["cycles"] == 1000


@pytest.mark.parametrize("key,value,error", [
    ("cycles", 1000.9, "P2071_RUNTIME_COUNTER_INVALID"),
    ("cycles", -1, "P2071_RUNTIME_COUNTER_INVALID"),
    ("closed_trades", True, "P2071_RUNTIME_METRIC_INVALID"),
    ("paper_mark_to_market_pnl", float("nan"), "P2071_RUNTIME_METRIC_INVALID"),
    ("final_mark_to_market_equity", float("inf"), "P2071_RUNTIME_METRIC_INVALID"),
    ("initial_equity", 0, "P2071_RUNTIME_EQUITY_INVALID"),
    ("drawdown_abs", 1, "P2071_RUNTIME_DRAWDOWN_INVALID"),
])
def test_invalid_paper_metrics_rejected(key, value, error):
    payload = baseline()
    payload["metrics"][key] = value
    with pytest.raises(ValueError, match=error):
        extract_runtime_metrics(payload)

def test_signed_drawdown_from_original_p2071_is_preserved():
    payload = baseline()
    payload["metrics"]["drawdown_abs"] = -953.05314
    payload["metrics"]["drawdown_pct"] = -0.00953053
    actual = extract_runtime_metrics(payload)
    assert actual["drawdown_abs"] == -953.05314
    assert actual["drawdown_pct"] == -0.00953053

def test_historical_drawdown_breach_survives_equity_recovery(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        RiskEngine, AnomalyDetection, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    payload=baseline()
    payload["metrics"]["drawdown_pct"]=-0.001
    payload["metrics"]["drawdown_abs"]=-100.
    payload["metrics"]["max_drawdown_pct"]=0.08
    runtime=extract_runtime_metrics(payload)
    assert RiskEngine().evaluate(runtime).status == "FAIL"
    assert "DRAWDOWN_OVER_LIMIT" in AnomalyDetection().evaluate(runtime).payload["anomalies"]


@pytest.mark.parametrize("value", [None, float("nan"), -0.01, 1.1])
def test_historical_drawdown_must_be_valid(value):
    payload=baseline()
    payload["metrics"]["max_drawdown_pct"]=value
    with pytest.raises(ValueError, match="P2071_MAX_DRAWDOWN"):
        extract_runtime_metrics(payload)

def test_p2089_runs_behavioral_failure_scenarios(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        FailureSimulation, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    result=FailureSimulation().evaluate(extract_runtime_metrics(baseline()))
    assert result.status == "PASS"
    assert len(result.payload) == 4
    assert all(result.payload.values())
    assert result.reason == "BEHAVIORAL_FAILURE_SIMULATION_OK"

def test_p2081_missing_inputs_do_not_create_evidence(tmp_path, monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        run_p2081_2090, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    out=tmp_path/"must_not_exist"
    with pytest.raises(FileNotFoundError):
        run_p2081_2090(str(tmp_path/"missing_portfolio.json"),
                       str(tmp_path/"missing_certification.json"), str(out))
    assert not out.exists()

def test_p2087_roundtrip_requires_entire_state(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRecovery, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    state={"program":"P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE",
           "runtime":{"cycles":1500,"drawdown_pct":-0.00953053},
           "specialists":3,"locks":dict(ABSOLUTE_LOCKS)}
    decision=PortfolioRecovery().evaluate(state)
    assert decision.status == "FAIL"
    assert decision.reason == "RUNTIME_REHYDRATION_NOT_VERIFIED"
    assert len(decision.payload["checkpoint_sha256"]) == 64
    assert decision.payload["durable_checkpoint_verified"] is True
    assert decision.payload["runtime_rehydration_verified"] is False
    assert decision.payload["restored_program"] == state["program"]

def test_p2087_rejects_nonfinite_checkpoint_state(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRecovery, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    with pytest.raises(ValueError):
        PortfolioRecovery().evaluate({"program":"P2081_2090", "runtime":{"equity":float("nan")}})

def test_p2087_persists_atomic_checkpoint_in_paper_directory(tmp_path, monkeypatch):
    import json
    import hashlib
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRecovery, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    state={"program":"P2081_2090_REALTIME_PORTFOLIO_GOVERNANCE",
           "runtime":{"cycles":1500},"locks":dict(ABSOLUTE_LOCKS)}
    directory=tmp_path/"checkpoints"
    decision=PortfolioRecovery().evaluate(state,str(directory))
    checkpoint=directory/"governance_state.json"
    assert checkpoint.is_file()
    assert not (directory/"governance_state.json.tmp").exists()
    raw=checkpoint.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==decision.payload["checkpoint_sha256"]
    assert json.loads(raw.decode("utf-8"))==state
    assert decision.payload["durable_checkpoint_verified"] is True
    assert decision.status=="FAIL"  # process rehydration is not verified

def test_p2085_p2086_refuse_undeclared_canonical_residual(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRebalancing, CapitalAllocation, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    specialists=[
        {"id":"s1","normalized_weight":0.5},
        {"id":"s2","normalized_weight":0.249856},
        {"id":"s3","normalized_weight":0.164287},
    ]
    rebalance=PortfolioRebalancing().evaluate(specialists)
    capital=CapitalAllocation().evaluate(specialists,99046.94686)
    assert rebalance.status=="FAIL"
    assert capital.status=="FAIL"
    assert "P2067_UNDECLARED_RESIDUAL" in rebalance.payload["reconciliation"]["error"]
    assert not rebalance.payload["allocation"]
    assert not capital.payload["allocation"]


def test_p2085_p2086_preserve_certified_non_equal_weights(monkeypatch):
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRebalancing, CapitalAllocation, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    specialists=[
        {"id":"s1","normalized_weight":0.5},
        {"id":"s2","normalized_weight":0.3},
        {"id":"s3","normalized_weight":0.2},
    ]
    rebalance=PortfolioRebalancing().evaluate(specialists)
    capital=CapitalAllocation().evaluate(specialists,100000.)
    assert rebalance.status=="PASS"
    assert rebalance.payload["allocation"]=={"s1":0.5,"s2":0.3,"s3":0.2}
    assert capital.status=="PASS"
    assert capital.payload["allocation"]=={"s1":50000.,"s2":30000.,"s3":20000.}

def test_p2087_never_overwrites_conflicting_checkpoint(tmp_path, monkeypatch):
    import json
    from app.runtime.p2081_2090_realtime_portfolio_governance import (
        PortfolioRecovery, ABSOLUTE_LOCKS,
    )
    for k,v in ABSOLUTE_LOCKS.items():
        monkeypatch.setenv(k,v)
    directory=tmp_path/"checkpoints"
    directory.mkdir()
    checkpoint=directory/"governance_state.json"
    original=json.dumps({"program":"historical_state","cycles":1500}).encode("utf-8")
    checkpoint.write_bytes(original)
    with pytest.raises(RuntimeError, match="P2087_EXISTING_CHECKPOINT_CONFLICT"):
        PortfolioRecovery().evaluate({"program":"different_state","cycles":1501},str(directory))
    assert checkpoint.read_bytes()==original
    assert not (directory/"governance_state.json.tmp").exists()
