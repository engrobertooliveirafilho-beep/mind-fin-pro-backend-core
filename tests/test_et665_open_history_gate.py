import json, tempfile, unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class OpenHistoryGateTest(unittest.TestCase):
    def manager(self, p):
        c=p/'config.json';c.write_text(json.dumps(default_ftmo_config()))
        return PaperTradingSessionManager(str(p/'session.json'),str(p/'ledger.jsonl'),str(c))
    def test_current_session_corruption_preserves_legacy_block(self):
        with tempfile.TemporaryDirectory() as d:
            m=self.manager(Path(d));m.open_session();m.record_trade_result(-10);m.close_session()
            lines=m.ledger_path.read_text().splitlines()
            e=json.loads(lines[1]);e['pnl']=-1000;lines[1]=json.dumps(e)
            m.ledger_path.write_text('\n'.join(lines)+'\n')
            self.assertEqual(m.open_session()['decision'],'BLOCK_LEDGER_MISMATCH')
    def test_older_session_corruption_blocks_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            m=self.manager(Path(d));m.open_session();m.record_trade_result(-10);m.close_session()
            m.open_session();m.close_session()
            lines=m.ledger_path.read_text().splitlines()
            e=json.loads(lines[1]);e['pnl']=-200;lines[1]=json.dumps(e)
            m.ledger_path.write_text('\n'.join(lines)+'\n')
            self.assertEqual(m.open_session()['decision'],'BLOCK_ACCOUNT_LEDGER_UNVERIFIED')
    def test_valid_history_allows_reopen(self):
        with tempfile.TemporaryDirectory() as d:
            m=self.manager(Path(d));m.open_session();m.close_session()
            self.assertEqual(m.open_session()['decision'],'SESSION_OPENED')
