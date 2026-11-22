import json
from pathlib import Path
from app.runtime.p2071_2080_realtime_paper_runtime import load_portfolio, SignalRuntime

SOURCE = Path(__file__).resolve().parents[1] / "data/specialists/P2066_2070/PORTFOLIO_FINAL_LOCKED_REALDNA.json"

def test_original_realdna_portfolio_is_preserved_without_truncation():
    raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    loaded = load_portfolio(str(SOURCE))
    assert loaded == raw
    assert [x["specialist_id"] for x in loaded] == [
        "XAUUSD_M1_REALDNA_0004",
        "XAUUSD_M1_REALDNA_0003",
        "XAUUSD_M1_REALDNA_0001",
    ]
    assert [x["logic_type"] for x in loaded] == [
        "RANGE_REVERSION", "MEAN_REVERSION", "TREND_PULLBACK"
    ]

def test_original_realdna_unsupported_strategies_cannot_emit_signals():
    runtime = SignalRuntime(load_portfolio(str(SOURCE)))
    assert runtime.unsupported_specialists == [
        "XAUUSD_M1_REALDNA_0003", "XAUUSD_M1_REALDNA_0001"
    ]

def test_original_portfolio_weights_preserved_not_silently_normalized():
    portfolio = load_portfolio(str(SOURCE))
    total = sum(x["portfolio_weight"] for x in portfolio)
    assert abs(total - 0.914143) < 1e-9
    assert total < 1.0  # Unallocated weight; do not infer an allocation policy.

def test_historical_pnl_not_misused_as_current_runtime_pnl():
    portfolio = load_portfolio(str(SOURCE))
    assert [x["total_pnl"] for x in portfolio] == [1269.77, 541.53, 356.07]
    assert all("paper_pnl" not in x and "realized_pnl" not in x for x in portfolio)


def test_original_historical_weights_fail_closed_before_paper_execution(tmp_path):
    import pytest
    from app.runtime.p2071_2080_realtime_paper_runtime import run_p2071_2080
    output = tmp_path / "must_not_exist"
    with pytest.raises(ValueError, match="P2067_UNDECLARED_RESIDUAL"):
        run_p2071_2080(str(SOURCE), str(output), cycles=1)
    assert not output.exists()


def test_historical_weights_are_distinct_from_normalized_weight():
    portfolio = load_portfolio(str(SOURCE))
    assert all("portfolio_weight" in item for item in portfolio)
    assert all("normalized_weight" not in item for item in portfolio)
