import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'app/runtime/capability_recovery_bridge.py'
spec = importlib.util.spec_from_file_location('bridge_r830', SOURCE)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)

class TestAncestorSymlinkFailClosed(unittest.TestCase):
    def test_symlink_parent_inside_root_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            actual = root / 'actual'; actual.mkdir()
            (actual / 'persistent_social_memory.py').write_text('def secret(): pass')
            (root / 'app/eldora').mkdir(parents=True)
            (root / 'app/eldora/core').symlink_to(actual, target_is_directory=True)
            x = bridge.capability_recovery_report(source_root=root)['modules'][0]
            self.assertEqual(x['static_inspection'], 'unavailable')
            self.assertEqual(x['functions'], [])
    def test_normal_file_parsed(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'app/eldora/core/persistent_social_memory.py'
            p.parent.mkdir(parents=True)
            p.write_text('async def future(): pass\nclass Engine: pass\nraise RuntimeError("must not execute")')
            x = bridge.capability_recovery_report(source_root=d)['modules'][0]
            self.assertEqual(x['static_inspection'], 'parsed_not_executed')
            self.assertEqual(x['functions'], ['future'])
            self.assertEqual(x['classes'], ['Engine'])
    def test_active_probe_forbidden(self):
        self.assertFalse(bridge.capability_recovery_report(execute_probes=True)['active_probe_allowed'])
    def test_not_allowlisted(self):
        x = bridge._static_module_declarations('app.unknown', '/tmp')
        self.assertEqual(x['static_inspection'], 'not_allowlisted')

if __name__ == '__main__': unittest.main()
