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

    def test_health_reports_degraded(self):
        with patch.object(wiring, "MODULES", ["missing.module"]), patch.object(wiring.importlib, "import_module", side_effect=ImportError("missing")):
            result = wiring.health()
        self.assertEqual(result["status"], "DEGRADED")


if __name__ == "__main__":
    unittest.main()
