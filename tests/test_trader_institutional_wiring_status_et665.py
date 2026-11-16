"""Offline regression for institutional PAPER wiring health semantics."""
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from app.runtime import mind_trader_institutional_wiring as wiring


class WiringStatusTests(unittest.TestCase):
    def test_missing_module_degraded(self):
        with patch.object(wiring, 'MODULES', ['missing.module']):
            with patch.object(wiring.importlib, 'import_module', side_effect=ImportError('not found')):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertEqual(result['imports_ok'], 0)
        self.assertEqual(result['mode'], 'PAPER_ONLY')

    def test_run_failure_degraded_even_when_import_succeeds(self):
        def broken_run(_payload):
            raise RuntimeError('failed')
        fake = SimpleNamespace(run=broken_run)
        with patch.object(wiring, 'MODULES', ['fixture.module']):
            with patch.object(wiring.importlib, 'import_module', return_value=fake):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result['imports_ok'], 1)
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertEqual(result['runs_ok'], 0)

    def test_healthy_module_operational(self):
        fake = SimpleNamespace(run=lambda _payload: {'ok': True}, health=lambda: {'ok': True})
        with patch.object(wiring, 'MODULES', ['fixture.module']):
            with patch.object(wiring.importlib, 'import_module', return_value=fake):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result['status'], 'operational')
        self.assertEqual(result['runs_ok'], 1)
        self.assertEqual(result['health_ok'], 1)

    def test_health_status_follows_runtime_status(self):
        with patch.object(wiring, 'MODULES', ['missing.module']):
            with patch.object(wiring.importlib, 'import_module', side_effect=ImportError('not found')):
                result = wiring.health()
        self.assertEqual(result['status'], 'DEGRADED')


    def test_unhealthy_health_payload_degraded(self):
        fake = SimpleNamespace(health=lambda: {'status': 'DEGRADED'}, run=lambda _payload: {'ok': True})
        with patch.object(wiring, 'MODULES', ['fixture.module']):
            with patch.object(wiring.importlib, 'import_module', return_value=fake):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertEqual(result['health_ok'], 0)

    def test_unhealthy_run_payload_degraded(self):
        fake = SimpleNamespace(health=lambda: {'ok': True}, run=lambda _payload: {'ok': False})
        with patch.object(wiring, 'MODULES', ['fixture.module']):
            with patch.object(wiring.importlib, 'import_module', return_value=fake):
                result = wiring.run_institutional_wiring({})
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertEqual(result['runs_ok'], 0)

    def test_empty_registry_degraded(self):
        with patch.object(wiring, 'MODULES', []):
            result = wiring.run_institutional_wiring({})
        self.assertEqual(result['status'], 'DEGRADED')
        self.assertEqual(result['modules_total'], 0)

if __name__ == '__main__':
    unittest.main()
