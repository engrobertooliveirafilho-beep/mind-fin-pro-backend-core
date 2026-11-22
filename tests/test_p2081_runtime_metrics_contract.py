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
    assert decision.status == "PASS"
    assert decision.payload["restored_program"] == state["program"]
