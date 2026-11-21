"""P8.48 offline PAPER session regressions; all I/O confined to temporary files."""
import tempfile
import json
import unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestSession(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = Path(self.tmp.name)
        cfg = p / "config.json"
        cfg.write_text(json.dumps(default_ftmo_config()))
        self.s = PaperTradingSessionManager(str(p / "session.json"),
                                            str(p / "ledger.jsonl"), str(cfg))
        self.assertEqual(self.s.open_session()["decision"], "SESSION_OPENED")

    def test_nan_risk(self):
        self.assertFalse(self.s.pre_trade_check(float("nan"))["allowed"])

    def test_negative_risk(self):
        self.assertFalse(self.s.pre_trade_check(-1)["allowed"])

    def test_zero_risk(self):
        self.assertFalse(self.s.pre_trade_check(0)["allowed"])

    def test_valid_risk(self):
        self.assertTrue(self.s.pre_trade_check(100)["allowed"])

    def test_positive_pnl_does_not_consume_loss_budget(self):
        self.s.record_trade_result(1000)
        self.assertTrue(self.s.pre_trade_check(4900)["allowed"])

    def test_nan_pnl_does_not_mutate(self):
        self.assertEqual(self.s.record_trade_result(float("nan"))["decision"], "BLOCK_INVALID_PNL")
        self.assertEqual(self.s.daily_summary()["trades"], 0)

    def test_loss_boundary(self):
        self.s.record_trade_result(-4900)
        self.assertFalse(self.s.pre_trade_check(101)["allowed"])

    def test_session_close(self):
        self.assertEqual(self.s.close_session()["decision"], "SESSION_CLOSED")
        self.assertFalse(self.s.pre_trade_check(100)["allowed"])

if __name__ == "__main__":
    unittest.main()
