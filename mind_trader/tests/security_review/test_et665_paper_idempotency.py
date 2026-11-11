"""ET665 isolated PAPER idempotency regressions. Run offline: python -m unittest mind_trader.tests.security_review.test_et665_paper_idempotency"""
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from mind_trader.app.risk.ftmo_ruleset import default_ftmo_config
from mind_trader.app.execution.paper_session import PaperTradingSessionManager

class PaperIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        config = root / "ftmo.json"
        config.write_text(json.dumps(default_ftmo_config()), encoding="utf-8")
        self.m = PaperTradingSessionManager(str(root/"session.json"), str(root/"day.jsonl"), str(config))
        self.assertEqual(self.m.open_session()["decision"], "SESSION_OPENED")
    def tearDown(self):
        self.tmp.cleanup()
    def test_duplicate_id_blocked(self):
        a = self.m.reserve_paper_order(100, "intent-1")
        b = self.m.reserve_paper_order(100, "intent-1")
        self.assertTrue(a["allowed"])
        self.assertFalse(b["allowed"])
        self.assertEqual(b["decision"], "BLOCK_DUPLICATE_CLIENT_ORDER_ID")
        self.assertEqual(len(self.m._read_session()["pending_paper_orders"]), 1)
    def test_restart_deduplicates(self):
        self.assertTrue(self.m.reserve_paper_order(100, "intent-2")["allowed"])
        restarted = PaperTradingSessionManager(str(self.m.session_path),str(self.m.ledger_path),str(self.m.ftmo_config_path))
        self.assertEqual(restarted.reserve_paper_order(100, "intent-2")["decision"],"BLOCK_DUPLICATE_CLIENT_ORDER_ID")
    def test_different_intents_allowed(self):
        self.assertTrue(self.m.reserve_paper_order(100,"intent-a")["allowed"])
        self.assertTrue(self.m.reserve_paper_order(100,"intent-b")["allowed"])
    def test_missing_id_fail_closed(self):
        self.assertFalse(self.m.reserve_paper_order(100)["allowed"])
    def test_concurrent_duplicate(self):
        barrier = threading.Barrier(2)
        results = []
        def worker():
            barrier.wait()
            results.append(self.m.reserve_paper_order(100,"concurrent-1"))
        threads=[threading.Thread(target=worker) for _ in range(2)]
        for t in threads:t.start()
        for t in threads:t.join(timeout=10)
        self.assertEqual(len(results),2)
        self.assertEqual(sum(x.get("allowed") is True for x in results),1)
    def test_write_failure_not_accepted(self):
        with patch.object(self.m,"_write_session",side_effect=OSError("disk full")):
            result=self.m.reserve_paper_order(100,"disk-full")
        self.assertFalse(result["allowed"])
        self.assertEqual(result["decision"],"BLOCK_PAPER_RESERVATION_ERROR")
    def test_settlement_cannot_duplicate(self):
        a=self.m.reserve_paper_order(100,"settle-once")
        self.assertEqual(self.m.settle_paper_order(a["reservation_id"],5)["decision"],"PAPER_RESERVATION_SETTLED")
        self.assertEqual(self.m.settle_paper_order(a["reservation_id"],5)["decision"],"BLOCK_SETTLEMENT_UNKNOWN_OR_DUPLICATE_ID")
        self.assertEqual(self.m.reserve_paper_order(100,"settle-once")["decision"],"BLOCK_DUPLICATE_CLIENT_ORDER_ID")

if __name__=="__main__":
    unittest.main()
