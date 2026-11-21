import unittest, tempfile, json
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestStreakAndAccount(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p=Path(self.tmp.name)
        cfg=p/"cfg.json"
        cfg.write_text(json.dumps(default_ftmo_config()))
        self.s=PaperTradingSessionManager(str(p/"session.json"),str(p/"ledger.jsonl"),str(cfg))
        self.assertEqual(self.s.open_session()["decision"],"SESSION_OPENED")

    def test_tampered_loss_streak(self):
        self.s.record_trade_result(-10)
        st=self.s._read_session()
        st["loss_streak"]=0
        self.s._write_session(st)
        self.assertEqual(self.s.pre_trade_check(100)["decision"],"BLOCK_LEDGER_MISMATCH")

    def test_tampered_persisted_account(self):
        st=self.s._read_session()
        st["account_id"]="FTMO_REAL"
        self.s._write_session(st)
        self.assertEqual(self.s.pre_trade_check(100)["decision"],"BLOCK_LEDGER_MISMATCH")

    def test_valid_streak(self):
        self.s.record_trade_result(-10)
        self.s.record_trade_result(-20)
        self.assertTrue(self.s.pre_trade_check(100)["allowed"])
        self.assertEqual(self.s.daily_summary()["loss_streak"],2)

if __name__ == "__main__":
    unittest.main()
