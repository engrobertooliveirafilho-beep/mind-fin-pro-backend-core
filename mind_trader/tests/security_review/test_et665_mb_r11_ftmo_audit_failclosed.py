"""ET665.MB.R11: FTMO audit fails closed for invalid trade and exposure."""
import pytest
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, audit_rule_application

BASE = {"symbol": "EURUSD", "daily_trades": 0, "daily_pnl": 0.0,
        "total_pnl": 0.0, "risk_amount": 100.0, "stop": 1.0}

@pytest.mark.parametrize("trade", [None, [], "bad", 1, True])
def test_nonmapping_trade_blocks(tmp_path, trade):
    result = audit_rule_application(trade, default_ftmo_config(), tmp_path / "audit.json")
    assert result["decision"] == "BLOCK_FTMO_SIMULATION"

@pytest.mark.parametrize("field,value", [
    ("risk_amount", None), ("risk_amount", True), ("risk_amount", -1),
    ("risk_amount", float("nan")), ("daily_pnl", "0"),
    ("daily_pnl", float("inf")), ("total_pnl", float("-inf")),
    ("daily_trades", True), ("daily_trades", -1), ("daily_trades", 0.5),
    ("stop", None), ("stop", "1"), ("stop", float("nan")),
    ("symbol", []), ("symbol", ""),
])
def test_invalid_trade_fields_block(tmp_path, field, value):
    trade = dict(BASE)
    trade[field] = value
    result = audit_rule_application(trade, default_ftmo_config(), tmp_path / "audit.json")
    assert result["decision"] == "BLOCK_FTMO_SIMULATION"

def test_finite_inputs_with_overflow_exposure_block(tmp_path):
    trade = dict(BASE, daily_pnl=1e308, risk_amount=1e308)
    result = audit_rule_application(trade, default_ftmo_config(), tmp_path / "audit.json")
    assert result["decision"] == "BLOCK_FTMO_SIMULATION"
    assert result["checks"]["risk_inside_daily_limit"] is False

def test_valid_paper_audit_remains_allowed(tmp_path):
    result = audit_rule_application(BASE, default_ftmo_config(), tmp_path / "audit.json")
    assert result["decision"] == "ALLOW_FTMO_SIMULATION"

def test_report_does_not_persist_raw_trade(tmp_path):
    path = tmp_path / "audit.json"
    trade = dict(BASE, private_token="SENSITIVE_MARKER")
    result = audit_rule_application(trade, default_ftmo_config(), path)
    assert result["decision"] == "ALLOW_FTMO_SIMULATION"
    assert "SENSITIVE_MARKER" not in path.read_text(encoding="utf-8")
