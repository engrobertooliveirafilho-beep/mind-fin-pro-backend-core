"""PAPER daily summary must fail closed on corrupt session or ledger."""
import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestSummarySafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        config = root / "config.json"
        config.write_text(json.dumps(default_ftmo_config()), encoding="utf-8")
        self.manager = PaperTradingSessionManager(str(root/"session.json"), str(root/"ledger.jsonl"), str(config))
        self.assertEqual(self.manager.open_session()["decision"], "SESSION_OPENED")
    def test_corrupt_json(self):
        self.manager.session_path.write_text("{", encoding="utf-8")
        self.assertEqual(self.manager.daily_summary()["decision"], "BLOCK_INVALID_SESSION_STATE")
    def test_non_object_json(self):
        self.manager.session_path.write_text("[]", encoding="utf-8")
        self.assertEqual(self.manager.daily_summary()["decision"], "BLOCK_INVALID_SESSION_STATE")
    def test_missing_ledger(self):
        self.manager.ledger_path.unlink()
        self.assertEqual(self.manager.daily_summary()["decision"], "BLOCK_LEDGER_MISMATCH")
    def test_valid_summary(self):
        self.assertEqual(self.manager.daily_summary()["decision"], "DAILY_SUMMARY")

if __name__ == "__main__":
    unittest.main()
