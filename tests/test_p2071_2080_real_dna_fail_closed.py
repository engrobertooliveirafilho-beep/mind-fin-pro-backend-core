import json
import pytest

from app.runtime.p2071_2080_realtime_paper_runtime import (
    load_portfolio, SignalRuntime, FeatureFrame
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

def test_all_specialists_are_preserved_and_unsupported_logic_is_not_reused(tmp_path):
    specialists = [
        {"id":"A","logic_type":"RANGE_REVERSION"},
        {"id":"B","logic_type":"MEAN_REVERSION"},
        {"id":"C","logic_type":"TREND_PULLBACK"},
    ]
    path = tmp_path / "portfolio.json"
    path.write_text(json.dumps({"specialists":specialists}), encoding="utf-8")
    loaded = load_portfolio(str(path))
    runtime = SignalRuntime(loaded)
    assert len(runtime.specialists) == 3
    assert runtime.unsupported_specialists == ["B", "C"]
    frame = FeatureFrame(1, "XAUUSD", 2400.0, 0.2, 0.0, 0.3, 0.2, 20.0, 10.0, 0.1)
    signals = runtime.generate(frame)
    assert [signal.specialist_id for signal in signals] == ["A"]
