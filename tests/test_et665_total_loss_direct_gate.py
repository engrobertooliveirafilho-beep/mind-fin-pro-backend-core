import unittest,tempfile,json
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TestDirectTotalLossGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        p=Path(self.tmp.name);c=p/'config.json';c.write_text(json.dumps(default_ftmo_config()))
        self.m=PaperTradingSessionManager(str(p/'session.json'),str(p/'ledger.jsonl'),str(c))
        self.m.open_session()
    def test_direct_pretrade_valid(self):
        self.assertTrue(self.m.pre_trade_check(100)['allowed'])
    def test_direct_pretrade_blocks_cumulative_loss(self):
        self.m.record_trade_result(-4900);self.m.close_session();self.m.open_session()
        self.m.record_trade_result(-4900);self.m.close_session();self.m.open_session()
        self.assertEqual(self.m.pre_trade_check(300)['decision'],'BLOCK_TOTAL_LOSS_LIMIT')
    def test_direct_pretrade_blocks_old_corruption(self):
        self.m.record_trade_result(-100);self.m.close_session();self.m.open_session()
        events=self.m.ledger_path.read_text().splitlines();e=json.loads(events[1]);e['pnl']=-500;events[1]=json.dumps(e)
        self.m.ledger_path.write_text('\n'.join(events)+'\n')
        self.assertEqual(self.m.pre_trade_check(100)['decision'],'BLOCK_ACCOUNT_LEDGER_UNVERIFIED')
