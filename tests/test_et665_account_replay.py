import json, tempfile, unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.paper.paper_ftmo_gateway import evaluate_paper_intent
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class AccountReplayTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        p=Path(self.tmp.name); self.audit=p/'audit.json'; c=p/'config.json'
        c.write_text(json.dumps(default_ftmo_config()))
        self.s=PaperTradingSessionManager(str(p/'session.json'),str(p/'ledger.jsonl'),str(c))
        self.s.open_session()
        self.intent={'mode':'PAPER','account_id':'PAPER_FTMO_SIM','side':'BUY','symbol':'EURUSD','risk_amount':100,'stop':1.1}
    def check(self,**kwargs):
        return evaluate_paper_intent(self.s,{**self.intent,**kwargs},str(self.audit))
    def test_ledger_authority_without_caller_total(self):
        self.assertEqual(self.check()['decision'],'ALLOW_PAPER_INTENT')
    def test_false_caller_total_blocked(self):
        self.assertEqual(self.check(account_total_pnl=100000)['decision'],'BLOCK_TOTAL_PNL_MISMATCH')
    def test_replay_across_sessions(self):
        self.s.record_trade_result(-100)
        self.s.close_session();self.s.open_session()
        self.assertEqual(self.s.account_total_pnl(),-100)
        self.assertEqual(self.check()['decision'],'ALLOW_PAPER_INTENT')
    def test_prior_session_corruption_blocks(self):
        self.s.record_trade_result(-100);self.s.close_session();self.s.open_session()
        events=[json.loads(x) for x in self.s.ledger_path.read_text().splitlines()]
        events[1]['pnl']=-9999
        self.s.ledger_path.write_text(''.join(json.dumps(x)+'\n' for x in events))
        self.assertEqual(self.check()['decision'],'BLOCK_ACCOUNT_LEDGER_UNVERIFIED')
    def test_prior_session_total_loss_blocks(self):
        self.s.record_trade_result(-4999);self.s.close_session();self.s.open_session()
        self.s.record_trade_result(-4999);self.s.close_session();self.s.open_session()
        self.assertEqual(self.check()['decision'],'BLOCK_TOTAL_LOSS_LIMIT')
if __name__=='__main__':unittest.main()
