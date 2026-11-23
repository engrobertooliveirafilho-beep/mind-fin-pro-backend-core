import unittest
from unittest.mock import patch
from types import SimpleNamespace
from app.runtime import mind_trader_institutional_wiring as wiring

class PaperInputGate(unittest.TestCase):
    def test_invalid_inputs_never_import(self):
        for payload in ("invalid", {"mode": "LIVE"}, {"mode": "DEMO"},
                        {"real_orders": True}, {"ftmo_real": "ENABLED"},
                        {"live_trading": True}, {"broker_execution": True},
                        {"financial_execution": True}, {"send_order": True},
                        {"mt5_order_send": True}, {"broker_api_call": True}):
            with self.subTest(payload=payload), patch.object(wiring.importlib, "import_module") as importer:
                with self.assertRaises(ValueError):
                    wiring.run(payload)
                importer.assert_not_called()

    def test_failed_health_prevents_run(self):
        calls = []
        module = SimpleNamespace(
            health=lambda: {"status": "DEGRADED"},
            run=lambda: calls.append("RUN") or {"status": "PASS"},
        )
        with patch.object(wiring, "MODULES", ["m"]):
            with patch.object(wiring.importlib, "import_module", return_value=module):
                result = wiring.run({"mode": "PAPER_ONLY"})
        self.assertEqual(calls, [])
        self.assertEqual(result["status"], "DEGRADED")
        self.assertFalse(result["results"][0]["run_available"])

    def test_health_exception_prevents_run(self):
        def fail():
            raise RuntimeError("offline")
        module = SimpleNamespace(health=fail, run=lambda: {"status": "PASS"})
        with patch.object(wiring, "MODULES", ["m"]):
            with patch.object(wiring.importlib, "import_module", return_value=module):
                result = wiring.run()
        self.assertEqual(result["status"], "DEGRADED")
        self.assertIn("health_gate_blocked_execution", result["results"][0]["error"])

    def test_engine_real_order_claim_cannot_pass(self):
        for evidence in ({"real_order_count": 1}, {"real_orders": True},
                         {"real_orders": "SENT"}):
            with self.subTest(evidence=evidence):
                module = SimpleNamespace(run=lambda: {"status": "PASS", **evidence})
                with patch.object(wiring, "MODULES", ["m"]):
                    with patch.object(wiring.importlib, "import_module", return_value=module):
                        result = wiring.run({"mode": "PAPER_ONLY"})
                self.assertEqual(result["status"], "DEGRADED")
                self.assertFalse(result["results"][0]["run_ok"])
                self.assertIn("real_order_evidence_blocked", result["results"][0]["error"])

    def test_paper_allowed(self):
        with patch.object(wiring, "MODULES", ["m"]):
            with patch.object(wiring.importlib, "import_module",
                              return_value=SimpleNamespace(run=lambda: {"status": "PASS"})):
                self.assertEqual(wiring.run({"mode": "PAPER_ONLY"})["status"], "operational")

if __name__ == "__main__":
    unittest.main()
