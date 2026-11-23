import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'app/runtime/capability_recovery_bridge.py'
spec = importlib.util.spec_from_file_location('bridge_r826', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class StaticInventoryTests(unittest.TestCase):
    def test_default_contract(self):
        r = m.capability_recovery_report()
        self.assertEqual(r['summary']['total'], 5)
        self.assertEqual(r['summary']['functionally_certified'], 0)
    def test_optin_still_disabled(self):
        self.assertFalse(m.capability_recovery_report(execute_probes=True)['active_probe_allowed'])
    def test_static_functions_classes_and_async(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'app/eldora/core/persistent_social_memory.py'
            p.parent.mkdir(parents=True)
            p.write_text('def safe(): pass\nasync def later(): pass\nclass Engine: pass\nraise RuntimeError("MUST NOT EXECUTE")\n')
            with patch.object(m.importlib, 'import_module', side_effect=AssertionError('import forbidden')):
                r = m.capability_recovery_report(source_root=d)
            x = r['modules'][0]
            self.assertEqual(x['functions'], ['later', 'safe'])
            self.assertEqual(x['classes'], ['Engine'])
            self.assertEqual(x['static_inspection'], 'parsed_not_executed')
            self.assertFalse(x['import_ok'])
    def test_missing_source_failclosed(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(m.capability_recovery_report(source_root=d)['modules'][0]['static_inspection'], 'unavailable')
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'app/eldora/core/persistent_social_memory.py'
            p.parent.mkdir(parents=True)
            external = Path(d)/'external.py'; external.write_text('def leaked(): pass')
            p.symlink_to(external)
            self.assertEqual(m.capability_recovery_report(source_root=d)['modules'][0]['static_inspection'], 'unavailable')
    def test_syntax_error_failclosed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'app/eldora/core/persistent_social_memory.py'
            p.parent.mkdir(parents=True); p.write_text('def (')
            self.assertEqual(m.capability_recovery_report(source_root=d)['modules'][0]['static_inspection'], 'unavailable')
    def test_no_active_helper_call(self):
        with patch.object(m, '_call_by_signature', side_effect=AssertionError('active')):
            self.assertEqual(m.capability_recovery_report()['summary']['with_successful_calls'], 0)
    def test_no_imports(self):
        with patch.object(m.importlib, 'import_module', side_effect=AssertionError('import')):
            self.assertEqual(m.capability_recovery_report()['summary']['import_ok'], 0)

if __name__ == '__main__': unittest.main()
