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

    def test_ftmo_config_drift_blocks_trade(self):
        config_path = Path(self.s.ftmo_config_path)
        config = json.loads(config_path.read_text())
        config["max_daily_loss"] = 4500
        config_path.write_text(json.dumps(config))
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_FTMO_CONFIG_CHANGED")

    def test_corrupt_trade_counter_blocks_trade(self):
        state = self.s._read_session()
        state["trades"] = -1
        self.s._write_session(state)
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_INVALID_SESSION_STATE")

    def test_corrupt_daily_limit_blocks_trade(self):
        state = self.s._read_session()
        state["max_daily_loss"] = 999999
        self.s._write_session(state)
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_INVALID_SESSION_STATE")

    def test_record_blocks_ftmo_config_drift(self):
        config_path = Path(self.s.ftmo_config_path)
        config = json.loads(config_path.read_text())
        config["max_daily_loss"] = 4500
        config_path.write_text(json.dumps(config))
        self.assertEqual(self.s.record_trade_result(-10)["decision"], "BLOCK_FTMO_CONFIG_CHANGED")
        self.assertEqual(self.s.daily_summary()["trades"], 0)

    def test_record_blocks_corrupted_counter(self):
        state = self.s._read_session()
        state["trades"] = -1
        self.s._write_session(state)
        self.assertEqual(self.s.record_trade_result(-10)["decision"], "BLOCK_INVALID_SESSION_STATE")

    def test_last_allowed_trade_can_settle(self):
        state = self.s._read_session()
        state["trades"] = state["max_daily_trades"]
        self.s._write_session(state)
        self.assertEqual(self.s.record_trade_result(-10)["decision"], "TRADE_RECORDED")

    def test_cumulative_pnl_overflow_no_mutation(self):
        self.assertEqual(self.s.record_trade_result(1e308)["decision"], "TRADE_RECORDED")
        self.assertEqual(self.s.record_trade_result(1e308)["decision"], "BLOCK_PNL_OVERFLOW")
        self.assertEqual(self.s.daily_summary()["trades"], 1)
        self.assertEqual(self.s.daily_summary()["daily_pnl"], 1e308)
        events = [json.loads(line) for line in Path(self.s.ledger_path).read_text().splitlines()]
        self.assertEqual(len(events), 2)

    def test_corrupt_session_blocks_reopen(self):
        Path(self.s.session_path).write_text("{", encoding="utf-8")
        self.assertEqual(self.s.open_session()["decision"], "BLOCK_INVALID_SESSION_STATE")
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_SESSION_CLOSED")

    def test_non_object_session_blocks_reopen(self):
        Path(self.s.session_path).write_text("[]", encoding="utf-8")
        self.assertEqual(self.s.open_session()["decision"], "BLOCK_INVALID_SESSION_STATE")

if __name__ == "__main__":
    unittest.main()
