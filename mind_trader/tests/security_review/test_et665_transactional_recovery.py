import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class TransactionalRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        p=Path(self.tmp.name)
        config=p/"config.json"
        config.write_text(json.dumps(default_ftmo_config()))
        self.manager=PaperTradingSessionManager(str(p/"session.json"),str(p/"day.jsonl"),str(config))
        self.assertEqual(self.manager.open_session()["decision"],"SESSION_OPENED")
        self.broker=p/"broker.jsonl"
        self.reservation=self.manager.reserve_paper_order(100,"intent-1")
        self.assertTrue(self.reservation["allowed"])
    def tearDown(self):
        self.tmp.cleanup()
    def fill(self, client_id="intent-1", token=None):
        row={"decision":"PAPER_ORDER_ACCEPTED","order":{"reservation_id":token or self.reservation["reservation_id"],"client_order_id":client_id},"fill":{"filled":True}}
        with self.broker.open("a") as f: f.write(json.dumps(row)+"\n")
    def test_recover_after_crash(self):
        self.fill()
        result=self.manager.recover_interrupted_paper_fills(self.broker)
        self.assertEqual(result["decision"],"PAPER_FILLS_ACKNOWLEDGED")
        self.assertTrue(self.manager._read_session()["pending_paper_orders"][0]["fill_recovered"])
        self.assertEqual(self.manager._read_session()["trades"],0)
    def test_restart_idempotent(self):
        self.fill()
        self.manager.recover_interrupted_paper_fills(self.broker)
        restarted=PaperTradingSessionManager(str(self.manager.session_path),str(self.manager.ledger_path),str(self.manager.ftmo_config_path))
        self.assertEqual(restarted.recover_interrupted_paper_fills(self.broker)["decision"],"PAPER_RECOVERY_NO_CHANGE")
        self.assertEqual(restarted.reconcile_paper_fills(self.broker)["decision"],"BLOCK_UNSETTLED_BROKER_FILL")
    def test_duplicate_fill_rejected(self):
        self.fill(); self.fill()
        self.assertEqual(self.manager.recover_interrupted_paper_fills(self.broker)["decision"],"BLOCK_RECOVERY_DUPLICATE_FILL")
    def test_mismatched_intent_rejected(self):
        self.fill(client_id="different")
        self.assertEqual(self.manager.recover_interrupted_paper_fills(self.broker)["decision"],"BLOCK_RECOVERY_ID_MISMATCH")
    def test_write_failure_no_acknowledgement(self):
        self.fill()
        with patch.object(self.manager,"_write_session",side_effect=OSError("disk full")):
            self.assertEqual(self.manager.recover_interrupted_paper_fills(self.broker)["decision"],"BLOCK_RECOVERY_WRITE_OR_LEDGER_ERROR")
        self.assertNotIn("fill_recovered",self.manager._read_session()["pending_paper_orders"][0])
    def test_corrupt_broker_ledger(self):
        self.broker.write_text("{bad")
        self.assertEqual(self.manager.recover_interrupted_paper_fills(self.broker)["decision"],"BLOCK_RECOVERY_WRITE_OR_LEDGER_ERROR")
    def test_no_broker_ledger_blocks(self):
        self.assertEqual(self.manager.recover_interrupted_paper_fills(self.broker)["decision"],"BLOCK_RECOVERY_NO_BROKER_LEDGER")

if __name__=="__main__":
    unittest.main()
