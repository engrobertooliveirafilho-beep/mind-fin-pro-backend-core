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
    assert "DUPLICATE_TRADE:1" in result["errors"]

def test_audit_real_flag_true_rejected():
    result = audit_trades([{**BASE, "real_execution_allowed": True}])
    assert "REAL_EXEC_FLAG_NOT_FALSE:0" in result["errors"]

def test_audit_unhashable_indices_fail_closed():
    result = audit_trades([{**BASE, "entry_i": []}])
    assert "INVALID_BAR_INDEX:0" in result["errors"]

def test_audit_overflow_integer_rejected_without_exception():
    result = audit_trades([{**BASE, "r": 10**10000}])
    assert "INVALID_NUMERIC:0:r" in result["errors"]

def test_audit_pnl_equity_mismatch_rejected():
    result = audit_trades([{**BASE, "capital_after": 105.0}])
    assert "PNL_EQUITY_MISMATCH:0" in result["errors"]

def test_audit_capital_chain_break_rejected():
    second = {**BASE, "signal_i": 5, "entry_i": 6, "exit_i": 8, "capital_before": 110.0, "capital_after": 111.0}
    result = audit_trades([BASE, second])
    assert "CAPITAL_CHAIN_BREAK:1" in result["errors"]

def test_montecarlo_invalid_runs_rejected():
    with pytest.raises(ValueError, match="INVALID_RUN_COUNT"):
        monte_carlo_from_trades([{"r": 1.0}], runs=0)

def test_montecarlo_nonfinite_r_rejected():
    with pytest.raises(ValueError, match="INVALID_TRADE_R"):
        monte_carlo_from_trades([{"r": math.inf}])

def test_montecarlo_overflow_integer_rejected():
    with pytest.raises(ValueError, match="INVALID_TRADE_R"):
        monte_carlo_from_trades([{"r": 10**10000}])

def test_montecarlo_empty_trades_is_deterministic():
    result = monte_carlo_from_trades([], initial_capital=100, runs=10)
    assert result["runs"] == 0 and result["p50_final"] == 100.0

def test_montecarlo_bootstrap_is_deterministic_and_replacement_based():
    trades = [{"r": 2.0}, {"r": -1.0}, {"r": 0.5}]
    first = monte_carlo_from_trades(trades, runs=100)
    second = monte_carlo_from_trades(trades, runs=100)
    assert first == second
    assert first["method"] == "bootstrap_with_replacement"
    assert first["runs"] == 100
