import json
import tempfile
import unittest
from pathlib import Path
from mind_trader.app.execution.paper_session import PaperTradingSessionManager
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config

class PaperReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        root=Path(self.temp.name)
        self.broker=root/"broker.jsonl"
        config=root/"config.json"
        config.write_text(json.dumps(default_ftmo_config()))
        self.manager=PaperTradingSessionManager(str(root/"session.json"),str(root/"day.jsonl"),str(config))
        self.assertEqual(self.manager.open_session()["decision"],"SESSION_OPENED")
    def tearDown(self):
        self.temp.cleanup()
    def write_fill(self, reservation_id):
        row={"decision":"PAPER_ORDER_ACCEPTED","order":{"reservation_id":reservation_id,"client_order_id":"test-intent"},"fill":{"filled":True}}
        with self.broker.open("a") as stream:
            stream.write(json.dumps(row)+"\n")
    def test_01_duplicate_reservation(self):
        self.assertTrue(self.manager.reserve_paper_order(100,"same-intent")["allowed"])
        self.assertEqual(self.manager.reserve_paper_order(100,"same-intent")["decision"],"BLOCK_DUPLICATE_CLIENT_ORDER_ID")
    def test_02_interrupted_fill_blocks(self):
        reservation=self.manager.reserve_paper_order(100,"fill-intent")
        self.write_fill(reservation["reservation_id"])
        self.assertEqual(self.manager.reconcile_paper_fills(self.broker)["decision"],"BLOCK_UNSETTLED_BROKER_FILL")
    def test_03_restart_blocks(self):
        reservation=self.manager.reserve_paper_order(100,"restart-intent")
        restarted=PaperTradingSessionManager(str(self.manager.session_path),str(self.manager.ledger_path),str(self.manager.ftmo_config_path))
        self.assertEqual(restarted.reserve_paper_order(100,"restart-intent")["decision"],"BLOCK_DUPLICATE_CLIENT_ORDER_ID")
        self.assertEqual(restarted.reconcile_paper_fills(self.broker)["decision"],"BLOCK_PENDING_PAPER_RESERVATIONS")
    def test_04_reconciliation_no_double_settlement(self):
        reservation=self.manager.reserve_paper_order(100,"settle-intent")
        self.assertEqual(self.manager.settle_paper_order(reservation["reservation_id"],5)["decision"],"PAPER_RESERVATION_SETTLED")
        self.assertEqual(self.manager.settle_paper_order(reservation["reservation_id"],5)["decision"],"BLOCK_SETTLEMENT_UNKNOWN_OR_DUPLICATE_ID")
        self.assertEqual(self.manager.reconcile_paper_fills(self.broker)["decision"],"PAPER_RECONCILIATION_CLEAN")
    def test_05_duplicate_broker_fill_blocks(self):
        reservation=self.manager.reserve_paper_order(100,"duplicate-fill")
        self.write_fill(reservation["reservation_id"])
        self.write_fill(reservation["reservation_id"])
        self.assertEqual(self.manager.reconcile_paper_fills(self.broker)["decision"],"BLOCK_DUPLICATE_BROKER_FILL")
    def test_06_corrupt_ledger_blocks(self):
        self.broker.write_text("{bad-json")
        self.assertEqual(self.manager.reconcile_paper_fills(self.broker)["decision"],"BLOCK_RECONCILIATION_LEDGER_ERROR")
    def test_07_uncorrelated_fill_blocks(self):
        self.broker.write_text(json.dumps({"decision":"PAPER_ORDER_ACCEPTED","order":{}})+"\n")
        self.assertEqual(self.manager.reconcile_paper_fills(self.broker)["decision"],"BLOCK_UNCORRELATED_BROKER_FILL")

if __name__=="__main__":
    unittest.main()
