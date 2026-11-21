import unittest
from unittest.mock import patch
from app.runtime import mind_trader_institutional_wiring as wiring

class InstitutionalWiringSafetyTests(unittest.TestCase):
    def test_health_does_not_call_run(self):
        with patch.object(wiring,"MODULES",["fake.module"]), patch.object(wiring.importlib,"import_module") as imp:
            m=imp.return_value
            m.run.side_effect=AssertionError("health executed run")
            result=wiring.health()
        self.assertFalse(result["execution_performed"])
        self.assertEqual(result["runs_ok"],0)
        self.assertEqual(result["status"],"IMPORTS_OK_UNCERTIFIED")
        m.run.assert_not_called()
    def test_health_import_failure_fails_closed(self):
        with patch.object(wiring,"MODULES",["missing.module"]), patch.object(wiring.importlib,"import_module",side_effect=ImportError("missing")):
            result=wiring.health()
        self.assertEqual(result["status"],"DEGRADED")
        self.assertEqual(result["imports_ok"],0)
    def test_wiring_failed_import_is_not_operational(self):
        with patch.object(wiring,"MODULES",["missing.module"]), patch.object(wiring.importlib,"import_module",side_effect=ImportError("missing")):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result["status"],"DEGRADED")
        self.assertEqual(result["imports_ok"],0)
    def test_wiring_import_only_not_certified(self):
        with patch.object(wiring,"MODULES",["fake.module"]), patch.object(wiring.importlib,"import_module",return_value=object()):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result["status"],"IMPORTS_OK_UNCERTIFIED")
        self.assertEqual(result["runs_ok"],0)
    def test_typeerror_does_not_retry_run(self):
        from unittest.mock import Mock
        module=Mock()
        module.run.side_effect=TypeError("internal failure after side effect")
        with patch.object(wiring,"MODULES",["fake.module"]), patch.object(wiring.importlib,"import_module",return_value=module):
            result=wiring.run_institutional_wiring({"mode":"PAPER_ONLY"})
        self.assertFalse(result["results"][0]["run_ok"])
        self.assertIn("run_error=",result["results"][0]["error"])
        module.run.assert_called_once_with({"mode":"PAPER_ONLY"})
