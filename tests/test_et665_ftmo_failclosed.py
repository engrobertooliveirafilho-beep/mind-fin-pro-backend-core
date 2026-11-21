"""Offline regressions for FTMO rule audit. No real orders, no network."""
import math
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.risk.ftmo_ruleset import (
    default_ftmo_config, validate_ftmo_config, audit_rule_application
)

class TestFTMOFailClosed(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "audit.json"
        self.config = default_ftmo_config()
    def audit(self, **overrides):
        trade = {"symbol": "EURUSD", "risk_amount": 100, "stop": 1, "daily_trades": 0}
        trade.update(overrides)
        return audit_rule_application(trade, self.config, self.path)["decision"]
    def test_valid_simulated_trade(self):
        self.assertEqual(self.audit(), "ALLOW_FTMO_SIMULATION")
    def test_negative_risk(self):
        self.assertEqual(self.audit(risk_amount=-1), "BLOCK_FTMO_SIMULATION")
    def test_nan_risk(self):
        self.assertEqual(self.audit(risk_amount=float("nan")), "BLOCK_FTMO_SIMULATION")
    def test_zero_risk(self):
        self.assertEqual(self.audit(risk_amount=0), "BLOCK_FTMO_SIMULATION")
    def test_nan_stop(self):
        self.assertEqual(self.audit(stop=float("nan")), "BLOCK_FTMO_SIMULATION")
    def test_negative_trade_count(self):
        self.assertEqual(self.audit(daily_trades=-1), "BLOCK_FTMO_SIMULATION")
    def test_bool_trade_count(self):
        self.assertEqual(self.audit(daily_trades=True), "BLOCK_FTMO_SIMULATION")
    def test_gain_does_not_count_as_loss(self):
        self.assertEqual(self.audit(daily_pnl=1000, risk_amount=4900), "ALLOW_FTMO_SIMULATION")
    def test_loss_boundary(self):
        self.assertEqual(self.audit(daily_pnl=-4900, risk_amount=101), "BLOCK_FTMO_SIMULATION")
    def test_nan_account_config(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, account_size=float("nan")))["valid"])
    def test_infinite_slippage(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, slippage=float("inf")))["valid"])
    def test_negative_spread(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, spread=-1))["valid"])

    def test_boolean_integer_limit(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, max_daily_trades=True))["valid"])
    def test_blank_allowed_symbol(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, allowed_symbols=[""]))["valid"])
    def test_invalid_restricted_symbol_type(self):
        self.assertFalse(validate_ftmo_config(dict(self.config, restricted_symbols=[123]))["valid"])
    def test_default_config_still_valid(self):
        self.assertTrue(validate_ftmo_config(self.config)["valid"])

if __name__ == "__main__":
    unittest.main()
