import json, tempfile, unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.paper.paper_ftmo_gateway import evaluate_paper_intent
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestOverlap(unittest.TestCase):
    def test_overlapping_sessions_block_account_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); c=p/'config.json'; c.write_text(json.dumps(default_ftmo_config()))
            m=PaperTradingSessionManager(str(p/'session.json'),str(p/'ledger.jsonl'),str(c))
            m.open_session()
            with m.ledger_path.open('a') as f:
                f.write(json.dumps({'type':'SESSION_OPENED','session_id':'forged','event_id':'forged-event','ftmo_config_hash':'a'*64})+'\n')
            self.assertIsNone(m.account_total_pnl())
            intent={'mode':'PAPER','account_id':'PAPER_FTMO_SIM','side':'BUY','symbol':'EURUSD','risk_amount':100,'stop':1.1}
            self.assertEqual(evaluate_paper_intent(m,intent,str(p/'audit.json'))['decision'],'BLOCK_ACCOUNT_LEDGER_UNVERIFIED')
    def test_sequential_sessions_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); c=p/'config.json'; c.write_text(json.dumps(default_ftmo_config()))
            m=PaperTradingSessionManager(str(p/'session.json'),str(p/'ledger.jsonl'),str(c))
            m.open_session(); m.record_trade_result(-10); m.close_session(); m.open_session()
            self.assertEqual(m.account_total_pnl(),-10)
