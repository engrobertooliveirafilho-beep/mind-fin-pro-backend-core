import math
import pytest
from app.runtime.p2614_real_fill_replay.audit import audit_trades
from app.runtime.p2614_real_fill_replay.montecarlo import monte_carlo_from_trades

BASE = {"signal_i": 1, "entry_i": 2, "exit_i": 4, "edge_id": "edge-1", "capital_before": 100.0, "capital_after": 101.0, "pnl_usd": 1.0, "r": 1.0, "real_execution_allowed": False}

def test_audit_valid_trade_passes():
    assert audit_trades([BASE])["passed"] is True

def test_audit_malformed_record_fails_closed():
    result = audit_trades([None])
    assert result["passed"] is False and "INVALID_TRADE_RECORD:0" in result["errors"]

def test_audit_missing_required_fields_fails_closed():
    result = audit_trades([{"edge_id": "edge-1"}])
    assert result["passed"] is False and any(e.startswith("MISSING_FIELDS") for e in result["errors"])

def test_audit_boolean_indices_rejected():
    result = audit_trades([{**BASE, "signal_i": True}])
    assert "INVALID_BAR_INDEX:0" in result["errors"]

def test_audit_nonfinite_numeric_rejected():
    result = audit_trades([{**BASE, "r": math.nan}])
    assert "INVALID_NUMERIC:0:r" in result["errors"]

def test_audit_duplicate_trade_rejected():
    result = audit_trades([BASE, BASE])
    assert "DUPLICATE_TRADE" in result["errors"]

def test_audit_real_flag_true_rejected():
    result = audit_trades([{**BASE, "real_execution_allowed": True}])
    assert "REAL_EXEC_FLAG_NOT_FALSE" in result["errors"]

def test_montecarlo_invalid_runs_rejected():
    with pytest.raises(ValueError, match="INVALID_RUN_COUNT"):
        monte_carlo_from_trades([{"r": 1.0}], runs=0)

def test_montecarlo_nonfinite_r_rejected():
    with pytest.raises(ValueError, match="INVALID_TRADE_R"):
        monte_carlo_from_trades([{"r": math.inf}])

def test_montecarlo_empty_trades_is_deterministic():
    assert monte_carlo_from_trades([], initial_capital=100, runs=10) == {"runs": 0, "p50_final": 100.0, "p95_dd": 0.0}

def test_audit_unhashable_indices_fail_closed():
    result = audit_trades([{**BASE, "entry_i": []}])
    assert result["passed"] is False and "INVALID_BAR_INDEX:0" in result["errors"]

def test_audit_overflow_integer_rejected_without_exception():
    result = audit_trades([{**BASE, "r": 10**10000}])
    assert result["passed"] is False and "INVALID_NUMERIC:0:r" in result["errors"]

def test_montecarlo_overflow_integer_rejected_without_exception():
    with pytest.raises(ValueError, match="INVALID_TRADE_R"):
        monte_carlo_from_trades([{"r": 10**10000}])
