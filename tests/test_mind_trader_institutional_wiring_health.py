import unittest
from unittest.mock import patch
from types import SimpleNamespace
from app.runtime import mind_trader_institutional_wiring as wiring


class WiringHealthTests(unittest.TestCase):
    def test_all_modules_healthy(self):
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: {"ok": True})
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "operational")

    def test_import_failure_degrades(self):
        with patch.object(wiring, "MODULES", ["missing.module"]), patch.object(wiring.importlib, "import_module", side_effect=ImportError("missing")):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")

    def test_missing_run_degrades(self):
        module = SimpleNamespace(health=lambda: {"status": "operational"})
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")

    def test_missing_health_degrades(self):
        module = SimpleNamespace(run=lambda payload: {"ok": True})
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")

    def test_degraded_module_health_blocks_operational(self):
        module = SimpleNamespace(health=lambda: {"status": "DEGRADED"}, run=lambda payload: {"ok": True})
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["health_ok"], 0)

    def test_error_run_response_blocks_operational(self):
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: {"error": "simulated failure"})
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["runs_ok"], 0)

    def test_health_does_not_execute_engines(self):
        calls = []
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: calls.append(payload))
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.health()
        self.assertEqual(result["status"], "operational")
        self.assertEqual(result["runs_ok"], 0)
        self.assertEqual(calls, [])

    def test_explicit_run_still_executes_engines(self):
        calls = []
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=lambda payload: (calls.append(payload), {"ok": True})[1])
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        self.assertEqual(result["status"], "operational")
        self.assertEqual(calls, [{"mode": "PAPER_ONLY"}])

    def test_internal_type_error_does_not_rerun_engine(self):
        calls = []
        def failing_run(payload):
            calls.append(payload)
            raise TypeError("internal failure")
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=failing_run)
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({"mode": "PAPER_ONLY"})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(len(calls), 1)
        self.assertIn("run_error=", result["results"][0]["error"])

    def test_no_argument_run_supported(self):
        calls = []
        def zero_arg_run():
            calls.append(True)
            return {"ok": True}
        module = SimpleNamespace(health=lambda: {"status": "operational"}, run=zero_arg_run)
        with patch.object(wiring, "MODULES", ["example.module"]), patch.object(wiring.importlib, "import_module", return_value=module):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "operational")
        self.assertEqual(len(calls), 1)

    def test_live_execution_rejected_before_import(self):
        for payload in ({"mode": "LIVE"}, {"execution_mode": "FTMO_REAL"}, {"real_orders": True}):
            with self.subTest(payload=payload), patch.object(wiring.importlib, "import_module") as importer:
                result = wiring.run_institutional_wiring(payload)
                self.assertEqual(result["status"], "BLOCKED")
                importer.assert_not_called()

    def test_non_dict_payload_rejected_before_import(self):
        with patch.object(wiring.importlib, "import_module") as importer:
            result = wiring.run_institutional_wiring("LIVE")
            self.assertEqual(result["error"], "INVALID_PAYLOAD")
            importer.assert_not_called()

    def test_unknown_mode_fails_closed_without_import(self):
        for payload in ({"mode": "production"}, {"account_mode": "FTMO"}, {"execution_mode": "live-trading"}, {"live": "true"}):
            with self.subTest(payload=payload), patch.object(wiring.importlib, "import_module") as importer:
                self.assertEqual(wiring.run_institutional_wiring(payload)["status"], "BLOCKED")
                importer.assert_not_called()

    def test_falsy_non_dict_payload_rejected(self):
        for payload in ([], "", 0, False):
            with self.subTest(payload=payload), patch.object(wiring.importlib, "import_module") as importer:
                self.assertEqual(wiring.run_institutional_wiring(payload)["error"], "INVALID_PAYLOAD")
                importer.assert_not_called()

    def test_health_reports_degraded(self):
        with patch.object(wiring, "MODULES", ["missing.module"]), patch.object(wiring.importlib, "import_module", side_effect=ImportError("missing")):
            result = wiring.health()
        self.assertEqual(result["status"], "DEGRADED")


if __name__ == "__main__":
    unittest.main()
