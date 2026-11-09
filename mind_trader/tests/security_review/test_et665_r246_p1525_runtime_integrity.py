"""ET665.R246 — offline P15.25 behavioral integrity, no broker or network."""
import contextlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[2] / 'app' / 'p1519_p1525_institutional_research_certification' / 'engine.py'

@contextlib.contextmanager
def cwd(where):
    before = Path.cwd()
    os.chdir(where)
    try:
        yield
    finally:
        os.chdir(before)

def load_engine():
    spec = importlib.util.spec_from_file_location('et665_r246_engine', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class CertificationIntegrity(unittest.TestCase):
    def test_untrusted_approval_never_certifies_persisted_artifacts(self):
        m = load_engine()
        source = {'symbol':'SYNTHETIC','timeframe':'H1','strategy':'sma','fast':5,'slow':21,
                  'dataset':'synthetic.csv','approved':True,'independent_approval':True,
                  'promoted':True,'status':'PAPER_RESEARCH_CERTIFIED'}
        trades = [{'return':.01} for _ in range(50)]
        curve = [1.01 ** (i+1) for i in range(50)]
        with tempfile.TemporaryDirectory(prefix='et665_r246_') as folder:
            with cwd(folder), patch.object(m, 'load_json', return_value=[source]), \
                 patch.object(m, 'reconstruct', return_value=(trades, curve)):
                returned = m.run()
                report_dir = Path('reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION')
                persisted = json.loads((report_dir/'institutional_certification.json').read_text())
                rows = json.loads((report_dir/'trade_reconstruction.json').read_text())
                self.assertEqual(returned, persisted)
                self.assertEqual(persisted['P15_25_CERTIFICATION'], 'RESEARCH_ONLY')
                self.assertEqual(persisted['INDEPENDENT_APPROVAL'], 'NOT_PROVEN')
                self.assertEqual(persisted['APPROVED_EDGES'], 0)
                self.assertEqual(persisted['REAL_ORDERS'], 'FORBIDDEN')
                self.assertEqual(rows[0]['status'], 'RESEARCH_ONLY')
                self.assertFalse(rows[0]['independent_approval'])
                self.assertEqual(rows[0]['real_orders'], 'FORBIDDEN')

    def test_malformed_trade_return_does_not_write_certification(self):
        m = load_engine()
        source = {'symbol':'SYNTHETIC','timeframe':'H1','strategy':'sma','fast':5,'slow':21,'dataset':'synthetic.csv'}
        with tempfile.TemporaryDirectory(prefix='et665_r246_') as folder:
            with cwd(folder), patch.object(m, 'load_json', return_value=[source]), \
                 patch.object(m, 'reconstruct', return_value=([{'return':'invalid'}], [1.0])):
                with self.assertRaises((TypeError,ValueError)):
                    m.run()
                self.assertFalse(Path('reports/P15.25_INSTITUTIONAL_RESEARCH_CERTIFICATION/institutional_certification.json').exists())

if __name__=='__main__':
    unittest.main()
