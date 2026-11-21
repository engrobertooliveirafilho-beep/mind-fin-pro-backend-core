"""Fail-closed last-event ledger reconciliation for PAPER-only sessions."""
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestLedgerReconciliation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p = Path(self.tmp.name)
        cfg = p / "cfg.json"
        cfg.write_text(json.dumps(default_ftmo_config()))
        self.s = PaperTradingSessionManager(str(p/"session.json"), str(p/"ledger.jsonl"), str(cfg))
        self.assertEqual(self.s.open_session()["decision"], "SESSION_OPENED")
    def test_deleted_ledger_blocks_trade(self):
        self.s.ledger_path.unlink()
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_LEDGER_MISMATCH")
    def test_truncated_ledger_blocks_record(self):
        self.s.ledger_path.write_text("{")
        self.assertEqual(self.s.record_trade_result(10)["decision"], "BLOCK_LEDGER_MISMATCH")
    def test_divergent_pnl_blocks_close(self):
        self.s.record_trade_result(10)
        state = self.s._read_session()
        state["daily_pnl"] = 12
        self.s._write_session(state)
        self.assertEqual(self.s.close_session()["decision"], "BLOCK_LEDGER_MISMATCH")
    def test_closed_session_corrupt_ledger_blocks_reopen(self):
        self.s.close_session()
        self.s.ledger_path.write_text("{")
        self.assertEqual(self.s.open_session()["decision"], "BLOCK_LEDGER_MISMATCH")

if __name__ == "__main__":
    unittest.main()
