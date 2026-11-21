import tempfile, json, unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestAccountIsolation(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        p=Path(self.tmp.name)
        cfg=p/"cfg.json"
        cfg.write_text(json.dumps(default_ftmo_config()))
        self.s=PaperTradingSessionManager(str(p/"session.json"),str(p/"ledger.jsonl"),str(cfg))

    def test_real_account_rejected(self):
        self.assertEqual(self.s.open_session("FTMO_REAL_123")["decision"],"BLOCK_NON_PAPER_ACCOUNT")
        self.assertFalse(self.s.session_path.exists())
        self.assertFalse(self.s.ledger_path.exists())

    def test_blank_account_rejected(self):
        self.assertEqual(self.s.open_session("")["decision"],"BLOCK_NON_PAPER_ACCOUNT")

    def test_paper_account_allowed(self):
        self.assertEqual(self.s.open_session("PAPER_FTMO_SIM")["decision"],"SESSION_OPENED")

if __name__ == "__main__":
    unittest.main()
