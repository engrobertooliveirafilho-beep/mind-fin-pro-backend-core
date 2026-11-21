"""ET665: institutional wiring must never report operational on failed modules."""
import unittest
from unittest.mock import patch
from app.runtime import mind_trader_institutional_wiring as wiring

class WiringHealthTests(unittest.TestCase):
    def test_import_failure_degrades_status(self):
        with patch.object(wiring.importlib, 'import_module', side_effect=ImportError('offline')):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result['status'],'DEGRADED')
        self.assertEqual(result['imports_ok'],0)
        self.assertEqual(result['real_orders'],'FORBIDDEN')
    def test_run_failure_degrades_status(self):
        class FailedModule:
            @staticmethod
            def run(payload):
                raise RuntimeError('paper engine unavailable')
        with patch.object(wiring.importlib,'import_module',return_value=FailedModule):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result['status'],'DEGRADED')
        self.assertEqual(result['runs_ok'],0)
    def test_missing_run_degrades_status(self):
        class EmptyModule:
            pass
        with patch.object(wiring.importlib,'import_module',return_value=EmptyModule):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result['status'],'DEGRADED')
        self.assertEqual(result['runs_ok'],0)
if __name__=='__main__':
    unittest.main()
