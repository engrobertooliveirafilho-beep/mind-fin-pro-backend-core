import pytest
from app.runtime.et665_r246_mtm_ensemble_audit import floating_equity, ensemble_feasibility

def bar(t, low, high, spread=0):
    return {"timestamp": "2026-01-01T10:%02d:00" % t, "low": low, "high": high, "spread": spread}

def position(side="BUY", **overrides):
    p = dict(entry_time="2026-01-01T10:00:00", exit_time="2026-01-01T10:30:00",
        side=side, lots=1, entry_fill=100, exit_fill=101,
        entry_cost_cash=0, exit_cost_cash=0, fx_rate=1,
        mode="PAPER_ONLY", real_orders="FORBIDDEN",
        ftmo_real="FORBIDDEN", real_execution_allowed=False)
    p.update(overrides)
    return p

def test_intrabar_loss_detected_even_when_exit_wins():
    bars = [bar(0, 100, 100), bar(15, 80, 110), bar(30, 101, 101)]
    out = floating_equity(bars, [position()], 1000, .01, 1)
    assert out["equity_end"] == 1001
    assert out["max_intrabar_adverse_drawdown_pct"] >= 2
    assert out["curve"][1]["floating_pnl"] == -20

def test_simultaneous_positions_marked_together():
    bars = [bar(0, 100, 100), bar(15, 90, 110, 50), bar(30, 101, 101)]
    out = floating_equity(bars, [position(), position(side="SELL", exit_fill=99)], 1000, .01, 1)
    assert out["curve"][1]["active_positions"] == 2
    assert out["curve"][1]["floating_pnl"] == -20.5

def test_real_mode_is_rejected():
    with pytest.raises(ValueError):
        floating_equity([bar(0,100,100),bar(30,101,101)],
                        [position(real_execution_allowed=True)],1000,.01,1)

def test_missing_cost_and_fx_fail_closed():
    with pytest.raises(ValueError):
        floating_equity([bar(0,100,100),bar(30,101,101)],
                        [position(exit_cost_cash=None)],1000,.01,1)

def member(eid, family, session="EU"):
    return dict(edge_id=eid, family=family, session=session, regime="TREND",
                timeframe="M15", ensemble_weight=1, status="ENSEMBLE_MEMBER")

def test_unique_contexts_fail_quorum():
    rows = [member(str(i),str(i),session=str(i)) for i in range(9)]
    result = ensemble_feasibility(rows)
    assert result["feasible_contexts"] == 0
    assert result["certified"] is False

def test_three_independent_families_feasible_not_certified():
    rows = [member("A","F1"),member("B","F2"),member("C","F3")]
    result = ensemble_feasibility(rows)
    assert result["feasible_contexts"] == 1
    assert result["certified"] is False and result["runtime_allowed"] is False

def test_same_family_rejected():
    rows = [member("A","F1"),member("B","F1"),member("C","F1")]
    assert ensemble_feasibility(rows)["feasible_contexts"] == 0
