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
    def test_internal_typeerror_does_not_retry(self):
        class Broken:
            calls=0
            @classmethod
            def run(cls,payload=None):
                cls.calls+=1
                raise TypeError('internal fault')
        with patch.object(wiring,'MODULES',['broken']), patch.object(wiring.importlib,'import_module',return_value=Broken):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(Broken.calls,1)
        self.assertEqual(result['status'],'DEGRADED')
        self.assertIn('internal fault',result['results'][0]['error'])
    def test_legacy_zero_argument_run(self):
        class Legacy:
            calls=0
            @classmethod
            def run(cls):
                cls.calls+=1
                return {'paper':True}
        with patch.object(wiring,'MODULES',['legacy']), patch.object(wiring.importlib,'import_module',return_value=Legacy):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(Legacy.calls,1)
        self.assertEqual(result['status'],'operational')
    def test_empty_registry_cannot_report_operational(self):
        with patch.object(wiring,'MODULES',[]):
            result=wiring.run_institutional_wiring({})
        self.assertEqual(result['status'],'DEGRADED')
        self.assertEqual(result['real_orders'],'FORBIDDEN')
        self.assertEqual(result['runs_ok'],0)
    def test_malformed_payload_rejected_before_import(self):
        with patch.object(wiring.importlib,'import_module') as importer:
            with self.assertRaises(TypeError):
                wiring.run_institutional_wiring('not a dict')
            importer.assert_not_called()
    def test_cycles_signature_cannot_receive_payload(self):
        class CyclicEngine:
            calls=0
            @classmethod
            def run(cls, cycles=30):
                cls.calls+=1
                return {'cycles':cycles}
        with patch.object(wiring,'MODULES',['cycles']), patch.object(wiring.importlib,'import_module',return_value=CyclicEngine):
            result=wiring.run_institutional_wiring({'symbol':'XAUUSD'})
        self.assertEqual(CyclicEngine.calls,0)
        self.assertEqual(result['status'],'DEGRADED')
        self.assertIn('UNSUPPORTED_RUN_CONTRACT',result['results'][0]['error'])
    def test_payload_signature_runs_once(self):
        class PayloadEngine:
            calls=0
            @classmethod
            def run(cls,payload):
                cls.calls+=1
                return {'mode':'PAPER_ONLY','symbol':payload['symbol']}
        with patch.object(wiring,'MODULES',['payload']), patch.object(wiring.importlib,'import_module',return_value=PayloadEngine):
            result=wiring.run_institutional_wiring({'symbol':'XAUUSD'})
        self.assertEqual(PayloadEngine.calls,1)
        self.assertEqual(result['status'],'operational')
if __name__=='__main__':
    unittest.main()
