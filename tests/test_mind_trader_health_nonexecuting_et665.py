"""ET665 offline regression: health checks must not dispatch PAPER motors."""
import unittest
from unittest.mock import patch
from app.runtime import mind_trader_institutional_wiring as w

class NonExecutingHealthTests(unittest.TestCase):
    def test_health_never_runs_engine(self):
        class Engine:
            calls=0
            @classmethod
            def run(cls,payload=None):
                cls.calls+=1
                raise AssertionError('engine should never run')
            @staticmethod
            def health(): return {'status':'healthy'}
        with patch.object(w,'MODULES',['engine']),patch.object(w.importlib,'import_module',return_value=Engine):
            result=w.health()
        self.assertEqual(Engine.calls,0)
        self.assertEqual(result['status'],'operational')
        self.assertEqual(result['runs_ok'],0)
    def test_missing_health_is_degraded(self):
        class Engine:
            @staticmethod
            def run(): return {'status':'healthy'}
        with patch.object(w,'MODULES',['engine']),patch.object(w.importlib,'import_module',return_value=Engine):
            result=w.health()
        self.assertEqual(result['status'],'DEGRADED')
    def test_failed_health_is_degraded(self):
        class Engine:
            @staticmethod
            def health(): raise RuntimeError('offline')
        with patch.object(w,'MODULES',['engine']),patch.object(w.importlib,'import_module',return_value=Engine):
            result=w.health()
        self.assertEqual(result['status'],'DEGRADED')
    def test_empty_modules_is_degraded(self):
        with patch.object(w,'MODULES',[]):
            result=w.health()
        self.assertEqual(result['status'],'DEGRADED')
if __name__=='__main__':unittest.main()
