import sys
import types
import unittest
from unittest.mock import patch

from app.runtime import mind_trader_institutional_wiring as wiring


class InstitutionalWiringSafetyTests(unittest.TestCase):
    def test_run_never_invokes_imported_module_run(self):
        called = []
        module = types.ModuleType("paper_test_motor")
        module.run = lambda payload: called.append(payload)
        module.health = lambda: {"status": "OK"}
        with patch.object(wiring, "MODULES", ["paper_test_motor"]):
            with patch.object(wiring.importlib, "import_module", return_value=module):
                result = wiring.run_institutional_wiring({"intent": "PAPER"})
        self.assertEqual(called, [])
        self.assertEqual(result["runs_ok"], 0)
        self.assertFalse(result["execution_performed"])
        self.assertEqual(result["status"], "IMPORTS_OK_UNCERTIFIED")

    def test_invalid_payload_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_PAYLOAD"):
            wiring.run_institutional_wiring("unsafe")
        for invalid in ("", 0, False, []):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "INVALID_PAYLOAD"):
                    wiring.run_institutional_wiring(invalid)

    def test_import_error_degrades_without_execution(self):
        with patch.object(wiring, "MODULES", ["missing_motor"]):
            with patch.object(wiring.importlib, "import_module", side_effect=ImportError("not found")):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result["status"], "DEGRADED")
        self.assertEqual(result["runs_ok"], 0)
        self.assertFalse(result["execution_performed"])


if __name__ == "__main__":
    unittest.main()
