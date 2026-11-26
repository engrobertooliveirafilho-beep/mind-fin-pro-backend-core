import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.runtime import mind_trader_institutional_wiring as wiring


class InstitutionalWiringFailClosedTests(unittest.TestCase):
    def setUp(self):
        self.safe_payload = {
            "mode": "PAPER_ONLY",
            "real_orders_allowed": False,
            "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN",
        }

    def test_live_payload_is_rejected_before_import(self):
        with patch.object(wiring.importlib, "import_module") as importer:
            with self.assertRaisesRegex(ValueError, "PAPER_ONLY_REQUIRED"):
                wiring.run_institutional_wiring({"mode": "LIVE"})
        importer.assert_not_called()

    def test_internal_typeerror_is_not_retried_without_payload(self):
        engine = SimpleNamespace(
            health=lambda: {"status": "operational"},
            run=Mock(side_effect=TypeError("internal contract failure")),
        )
        with patch.object(wiring, "MODULES", ["fake.engine"]), \
             patch.object(wiring.importlib, "import_module", return_value=engine):
            result = wiring.run_institutional_wiring(self.safe_payload)
        self.assertEqual(engine.run.call_count, 1)
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertEqual(result["status"], "DEGRADED")
        self.assertIn("internal contract failure", result["results"][0]["error"])

    def test_unsupported_run_signature_fails_closed(self):
        def run(required_a, required_b):
            return {"status": "operational"}
        engine = SimpleNamespace(health=lambda: {"status": "operational"}, run=run)
        with patch.object(wiring, "MODULES", ["fake.engine"]), \
             patch.object(wiring.importlib, "import_module", return_value=engine):
            result = wiring.run_institutional_wiring(self.safe_payload)
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertEqual(result["status"], "DEGRADED")
        self.assertIn("UNSUPPORTED", result["results"][0]["error"])

    def test_unhealthy_run_cannot_report_operational(self):
        engine = SimpleNamespace(
            health=lambda: {"status": "operational"},
            run=lambda payload: {"status": "FAILED"},
        )
        with patch.object(wiring, "MODULES", ["fake.engine"]), \
             patch.object(wiring.importlib, "import_module", return_value=engine):
            result = wiring.run_institutional_wiring(self.safe_payload)
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertEqual(result["status"], "DEGRADED")

    def test_health_probe_does_not_execute_engine(self):
        run = Mock(return_value={"status": "operational"})
        engine = SimpleNamespace(health=lambda: {"status": "operational"}, run=run)
        with patch.object(wiring, "MODULES", ["fake.engine"]), \
             patch.object(wiring.importlib, "import_module", return_value=engine):
            result = wiring.health()
        run.assert_not_called()
        self.assertEqual(result["runs_ok"], 0)
        self.assertEqual(result["status"], "operational")

    def test_import_failure_degrades_aggregate(self):
        with patch.object(wiring, "MODULES", ["missing.engine"]), \
             patch.object(wiring.importlib, "import_module", side_effect=ImportError("missing")):
            result = wiring.run_institutional_wiring(self.safe_payload)
        self.assertEqual(result["imports_ok"], 0)
        self.assertEqual(result["status"], "DEGRADED")


if __name__ == "__main__":
    unittest.main()
