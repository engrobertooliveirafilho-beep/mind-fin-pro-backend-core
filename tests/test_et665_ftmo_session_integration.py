"""Offline integration of P8.46 FTMO rules and P8.48 PAPER session, no broker calls."""
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config, audit_rule_application
from mind_trader.app.paper.paper_session import PaperTradingSessionManager

class TestFTMOSessionIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = default_ftmo_config()
        self.config_path = self.root / "config.json"
        self.config_path.write_text(json.dumps(self.config), encoding="utf-8")
        self.manager = PaperTradingSessionManager(
            str(self.root / "session.json"),
            str(self.root / "ledger.jsonl"),
            str(self.config_path))
    def audit(self, **overrides):
        trade = {"symbol":"EURUSD","risk_amount":100,"stop":1.05,
                 "daily_trades":0,"daily_pnl":0,"total_pnl":0}
        trade.update(overrides)
        return audit_rule_application(trade,self.config,self.root/"audit.json")
    def test_valid_simulation_and_session(self):
        self.assertEqual(self.manager.open_session()["decision"],"SESSION_OPENED")
        self.assertEqual(self.audit()["decision"],"ALLOW_FTMO_SIMULATION")
        self.assertTrue(self.manager.pre_trade_check(100)["allowed"])
        self.assertEqual(self.manager.record_trade_result(-50)["decision"],"TRADE_RECORDED")
        self.assertEqual(self.manager.daily_summary()["daily_pnl"],-50)
        self.assertEqual(self.manager.close_session()["decision"],"SESSION_CLOSED")
    def test_negative_risk_blocked_by_both(self):
        self.manager.open_session()
        self.assertEqual(self.audit(risk_amount=-10)["decision"],"BLOCK_FTMO_SIMULATION")
        self.assertFalse(self.manager.pre_trade_check(-10)["allowed"])
    def test_nan_risk_blocked_by_both(self):
        self.manager.open_session()
        self.assertEqual(self.audit(risk_amount=float("nan"))["decision"],"BLOCK_FTMO_SIMULATION")
        self.assertFalse(self.manager.pre_trade_check(float("nan"))["allowed"])
    def test_invalid_ftmo_config_blocks_session(self):
        self.config["account_size"] = float("nan")
        self.config_path.write_text(json.dumps(self.config))
        self.assertEqual(self.manager.open_session()["decision"],"BLOCK_SESSION_INVALID_FTMO_CONFIG")
    def test_daily_loss_limit_consistent(self):
        self.manager.open_session()
        self.manager.record_trade_result(-4900)
        self.assertEqual(self.audit(daily_pnl=-4900,risk_amount=101)["decision"],"BLOCK_FTMO_SIMULATION")
        self.assertFalse(self.manager.pre_trade_check(101)["allowed"])
    def test_gain_not_counted_as_loss(self):
        self.manager.open_session()
        self.manager.record_trade_result(1000)
        self.assertEqual(self.audit(daily_pnl=1000,risk_amount=4900)["decision"],"ALLOW_FTMO_SIMULATION")
        self.assertTrue(self.manager.pre_trade_check(4900)["allowed"])

if __name__ == "__main__":
    unittest.main()
