import json
import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import (
    load_portfolio, SignalRuntime, FeatureFrame, promote_p2080_if_ready
)

def test_missing_portfolio_fails_closed(tmp_path):
    path = tmp_path / "missing.json"
    path.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(ValueError, match="REALDNA_PORTFOLIO_MISSING_OR_EMPTY"):
        load_portfolio(str(path))

def test_duplicate_specialist_ids_fail_closed(tmp_path):
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists":[{"id":"A","type":"RANGE_REVERSION"},{"id":"A","type":"RANGE_REVERSION"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="REALDNA_SPECIALIST_ID_DUPLICATE"):
        load_portfolio(str(path))

def test_all_specialists_preserved_and_unsupported_logic_not_reused(tmp_path):
    specialists = [
        {"id":"A","logic_type":"RANGE_REVERSION"},
        {"id":"B","logic_type":"MEAN_REVERSION"},
        {"id":"C","logic_type":"TREND_PULLBACK"},
    ]
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists":specialists}), encoding="utf-8")
    runtime = SignalRuntime(load_portfolio(str(path)))
    assert len(runtime.specialists) == 3
    assert runtime.unsupported_specialists == ["B", "C"]
    frame = FeatureFrame(1, "XAUUSD", 2400.0, 0.2, 0.0, 0.3, 0.2, 20.0, 10.0, 0.1)
    assert [x.specialist_id for x in runtime.generate(frame)] == ["A"]

def test_synthetic_feed_never_certifies_realtime():
    status = {key:"PASS" for key in [
        "P2072_REALTIME_FEATURE_BUILDER","P2073_SIGNAL_RUNTIME",
        "P2074_PAPER_PORTFOLIO_EXECUTOR","P2075_RUNTIME_MONITOR",
        "P2076_EXTENDED_RUNTIME_VALIDATION","P2077_MULTI_SESSION_RUNTIME",
        "P2078_RECOVERY_VALIDATION","P2079_RUNTIME_PERSISTENCE"]}
    status["P2071_REALTIME_DATA_FEED_BRIDGE"] = "PASS_SIMULATED_ONLY"
    result = promote_p2080_if_ready(status)
    assert result["P2080_REALTIME_RUNTIME_CERTIFICATION"] == "PASS_SIMULATION_SCOPE_ONLY"
