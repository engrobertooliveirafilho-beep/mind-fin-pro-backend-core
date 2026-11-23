import unittest
from unittest.mock import patch
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "app" / "runtime" / "capability_recovery_bridge.py"
spec = importlib.util.spec_from_file_location("r818_capability_bridge", SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TestR817(unittest.TestCase):
    def test_helper_never_calls(self):
        def bad(): raise AssertionError('executed')
        self.assertFalse(m._call_by_signature(bad)['ok'])

    def test_helper_skips(self): self.assertTrue(m._call_by_signature(lambda: 1)['skipped'])
    def test_helper_reason(self): self.assertEqual(m._call_by_signature(None)['reason'], 'active_probe_disabled')
    def test_inspect_no_import(self):
        with patch.object(m.importlib, 'import_module', side_effect=AssertionError('import')):
            self.assertFalse(m.inspect_capability_module('x')['import_ok'])
    def test_inspect_empty(self): self.assertEqual(m.inspect_capability_module('x')['functions'], [])
    def test_inspect_not_certified(self): self.assertEqual(m.inspect_capability_module('x')['certification'], 'not_tested')
    def test_default(self): self.assertEqual(m.capability_recovery_report()['mode'], 'declared_only')
    def test_optin_disabled(self): self.assertFalse(m.capability_recovery_report(execute_probes=True)['active_probe_allowed'])
    def test_no_import_on_report(self):
        with patch.object(m.importlib, 'import_module', side_effect=AssertionError('import')):
            self.assertEqual(m.capability_recovery_report()['summary']['with_successful_calls'], 0)
    def test_all_five(self): self.assertEqual(len(m.capability_recovery_report()['modules']), 5)
    def test_identity(self): self.assertEqual(m.capability_recovery_report('u', 'm')['user_id'], 'u')
    def test_no_functional_certification(self): self.assertEqual(m.capability_recovery_report()['summary']['functionally_certified'], 0)


if __name__ == '__main__':
    unittest.main()
