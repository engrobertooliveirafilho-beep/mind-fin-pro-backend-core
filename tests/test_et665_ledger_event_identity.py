import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class LedgerEventIdentity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        p = Path(self.temp.name)
        cfg = p / "config.json"
        cfg.write_text(json.dumps(default_ftmo_config()))
        self.s = PaperTradingSessionManager(str(p/"session.json"), str(p/"ledger.jsonl"), str(cfg))
        self.assertEqual(self.s.open_session()["decision"], "SESSION_OPENED")

    def test_duplicate_event_id_across_sessions_blocks(self):
        self.assertEqual(self.s.record_trade_result(10)["decision"], "TRADE_RECORDED")
        events = [json.loads(line) for line in self.s.ledger_path.read_text().splitlines()]
        events[1]["event_id"] = events[0]["event_id"]
        self.s.ledger_path.write_text("".join(json.dumps(e)+"\n" for e in events))
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_LEDGER_MISMATCH")

    def test_foreign_event_without_id_blocks(self):
        with self.s.ledger_path.open("a") as f:
            f.write(json.dumps({"type":"TRADE_RESULT","session_id":"OTHER"})+"\n")
        self.assertEqual(self.s.pre_trade_check(100)["decision"], "BLOCK_LEDGER_MISMATCH")

    def test_valid_events_still_allow(self):
        self.assertTrue(self.s.pre_trade_check(100)["allowed"])

if __name__ == "__main__":
    unittest.main()
