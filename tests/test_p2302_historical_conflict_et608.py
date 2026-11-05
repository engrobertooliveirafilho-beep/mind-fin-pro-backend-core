from audits.p2302_historical_conflict_detector import conflicting_groups

COLUMNS = "signal_id,symbol,action,lot,timestamp,candle_key,timeframe,family,confirmation,exit_model,dedup_key,mode,real_orders,ftmo_real,status"
ROWS = [
    "P2302_5ed23464b49d,GER40,BUY,0.01,2026-06-22T12:39:41,20260622_11_H1,H1,LIQUIDITY_SWEEP_REVERSAL,MTF_REQUIRED,TIME_EXIT,100cb91687e9861b,PAPER_ONLY,FORBIDDEN,FORBIDDEN,PAPER_SIGNAL_GENERATED",
    "P2302_40170ec445d9,GER40,BUY,0.01,2026-06-22T12:39:41,20260622_11_H1,H1,LIQUIDITY_SWEEP_REVERSAL,VOLATILITY_REQUIRED,TIME_EXIT,be58a5740c041b7a,PAPER_ONLY,FORBIDDEN,FORBIDDEN,PAPER_SIGNAL_GENERATED",
    "P2302_f809caced9c0,GER40,SELL,0.01,2026-06-22T12:39:41,20260622_11_H1,H1,VWAP_REVERSION,MTF_REQUIRED,TIME_EXIT,0bd1bf3ad2fe6b8a,PAPER_ONLY,FORBIDDEN,FORBIDDEN,PAPER_SIGNAL_GENERATED",
    "P2302_0896f58d4d8c,GER40,SELL,0.01,2026-06-22T12:39:41,20260622_11_H1,H1,VWAP_REVERSION,VOLATILITY_REQUIRED,TIME_EXIT,93e8c9180978c1d4,PAPER_ONLY,FORBIDDEN,FORBIDDEN,PAPER_SIGNAL_GENERATED",
]
def test_original_four_candidate_conflict_blocks_all_emission():
    conflicts = conflicting_groups("\n".join([COLUMNS, *ROWS]))
    assert len(conflicts) == 1
    assert conflicts[0]["candidate_count"] == 4
    assert conflicts[0]["actions"] == ["BUY", "SELL"]
    assert conflicts[0]["emit_allowed"] is False
    assert conflicts[0]["paper_lot"] == 0.0
    assert conflicts[0]["real_orders"] == "FORBIDDEN"

def test_different_candle_directions_are_not_conflicts():
    rows = [ROWS[0], ROWS[2].replace("20260622_11_H1", "20260622_12_H1")]
    assert conflicting_groups("\n".join([COLUMNS, *rows])) == []

def test_missing_identity_rejected():
    import pytest
    with pytest.raises(ValueError, match="MISSING_CANDLE_IDENTITY"):
        conflicting_groups("symbol,timeframe,candle_key,action\nGER40,H1,,BUY")

def test_non_direction_rejected():
    import pytest
    with pytest.raises(ValueError, match="INVALID_ACTION"):
        conflicting_groups("symbol,timeframe,candle_key,action\nGER40,H1,x,HOLD")
