"""Regression: DEMO pre-trade governor must fail closed for malformed risk inputs."""
import math
import pytest
from mind_trader.app.p69_73_mt5_ftmo_demo_governor.engine import p71_pre_trade_governor

STATE = {"balance": 100000, "equity": 100000, "daily_pnl": 0, "total_pnl": 0, "trading_days": 0}

@pytest.mark.parametrize("risk", [-0.001, 0.0, float("nan"), float("inf"), -float("inf"), "0.001", None, True, 0.1])
def test_malformed_or_excessive_risk_is_blocked(risk):
    result = p71_pre_trade_governor(STATE, risk, "DEMO")
    assert result["decision"] == "BLOCK_TRADE"
    assert "RISK_PER_TRADE_INVALID_OR_EXCESSIVE" in result["block_reasons"]
    assert result["REAL_ORDERS"] == "FORBIDDEN"

def test_valid_small_demo_risk_remains_simulation_only():
    result = p71_pre_trade_governor(STATE, 0.001, "DEMO")
    assert result["decision"] == "ALLOW_DEMO_TRADE"
    assert result["REAL_ORDERS"] == "FORBIDDEN"
    assert result["MT5_REAL"] == "FORBIDDEN"

def test_real_account_rejected_even_with_valid_risk():
    result = p71_pre_trade_governor(STATE, 0.001, "REAL")
    assert result["decision"] == "BLOCK_TRADE"
