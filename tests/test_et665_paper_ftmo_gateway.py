import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.paper.paper_session import PaperTradingSessionManager
from mind_trader.app.paper.paper_ftmo_gateway import evaluate_paper_intent
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class GatewayTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.audit=root/"audit.json"
        config=root/"config.json"
        config.write_text(json.dumps(default_ftmo_config()))
        self.session=PaperTradingSessionManager(str(root/"session.json"),str(root/"ledger.jsonl"),str(config))
        self.session.open_session()
        self.intent={"mode":"PAPER","account_id":"PAPER_FTMO_SIM","side":"BUY","symbol":"EURUSD","risk_amount":100,"stop":1.1,"account_total_pnl":0.0}
    def decide(self,**kwargs):
        return evaluate_paper_intent(self.session,{**self.intent,**kwargs},str(self.audit))
    def test_missing_account_total_blocks(self):
        intent=dict(self.intent)
        intent.pop("account_total_pnl")
        result=evaluate_paper_intent(self.session,intent,str(self.audit))
        self.assertEqual(result["decision"],"BLOCK_TOTAL_PNL_UNVERIFIED")
        self.assertFalse(self.audit.exists())

    def test_nonfinite_account_total_blocks(self):
        self.assertEqual(self.decide(account_total_pnl=float("nan"))["decision"],"BLOCK_TOTAL_PNL_UNVERIFIED")

    def test_cumulative_loss_blocks_even_when_daily_loss_is_zero(self):
        self.assertEqual(self.decide(account_total_pnl=-9950)["decision"],"BLOCK_FTMO_RULES")

    def test_valid_paper_intent(self):
        self.assertEqual(self.decide()["decision"],"ALLOW_PAPER_INTENT")
    def test_real_account_blocked_without_audit(self):
        self.assertEqual(self.decide(account_id="FTMO_REAL")["decision"],"BLOCK_NON_PAPER_INTENT")
        self.assertFalse(self.audit.exists())
    def test_live_mode_blocked(self):
        self.assertEqual(self.decide(mode="LIVE")["decision"],"BLOCK_NON_PAPER_INTENT")
    def test_restricted_symbol(self):
        self.assertEqual(self.decide(symbol="INVALID")["decision"],"BLOCK_FTMO_RULES")
    def test_invalid_stop(self):
        self.assertEqual(self.decide(stop=None)["decision"],"BLOCK_FTMO_RULES")
    def test_session_config_drift(self):
        config=Path(self.session.ftmo_config_path)
        c=json.loads(config.read_text())
        c["max_daily_loss"]=4500
        config.write_text(json.dumps(c))
        self.assertEqual(self.decide()["decision"],"BLOCK_FTMO_CONFIG_CHANGED")
    def test_closed_session(self):
        self.session.close_session()
        self.assertEqual(self.decide()["decision"],"BLOCK_NO_OPEN_SESSION")
    def test_no_order_dispatch(self):
        result=self.decide()
        self.assertEqual(result["production"],"BLOCKED")
        self.assertNotIn("order_id",result)

if __name__=="__main__":
    unittest.main()
