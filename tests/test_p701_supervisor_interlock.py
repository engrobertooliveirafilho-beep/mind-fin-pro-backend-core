import json,os,unittest
from pathlib import Path
from app.runtime.p701_supervisor_interlock import supervise,BLOCKS

def allocation(**kw):
    r=dict(edge_id='x',asset='A',timeframe='H1',family='F',risk_pct=.001,allocation_status='ALLOCATED_SIMULATED',order_sent=False,**BLOCKS);r.update(kw);return r
def report(**kw):
    r=dict(TOTAL_ALLOCATED_RISK_PCT=.001,ORDER_SENT=False,**BLOCKS);r.update(kw);return r
def supervised(**kw):
    r=dict(edge_id='x',risk_pct=.001,shadow_only=True,execution_allowed=False,health='GREEN',**BLOCKS);r.update(kw);return r
class TestSupervisor(unittest.TestCase):
    def test_safe(self):self.assertEqual(supervise([allocation()],report(),[supervised()])['supervised'][0]['supervisor_status'],'ACTIVE')
    def test_excess(self):
        out=supervise([allocation(risk_pct=.006)],report(TOTAL_ALLOCATED_RISK_PCT=.006),[supervised(risk_pct=.006)])
        self.assertEqual(out['supervised'][0]['supervisor_status'],'BLOCKED_RISK')
    def test_real(self):
        with self.assertRaises(ValueError):supervise([allocation()],report(),[supervised(REAL_ORDERS='ALLOWED')])
    def test_execution(self):
        with self.assertRaises(ValueError):supervise([allocation()],report(),[supervised(execution_allowed=True)])
    def test_mismatch(self):
        with self.assertRaises(ValueError):supervise([allocation()],report(),[supervised(risk_pct=.002)])
    def test_missing(self):
        with self.assertRaises(ValueError):supervise([allocation()],report(),[])
    def test_no_certification(self):self.assertFalse(supervise([allocation()],report(),[supervised()])['operationally_certified'])
    @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical files required')
    def test_historical_fail_closed(self):
        root=Path(os.environ['ELDORA_HISTORICAL_DIR'])
        def read(name):return json.loads((root/name).read_text())
        out=supervise(read('p601_700_allocation.json'),read('p601_700_master_report.json'),read('p701_supervised_edges.json'))
        self.assertEqual(out['risk_audit']['status'],'REJECTED_CAP')
        self.assertTrue(all(r['supervisor_status']=='BLOCKED_RISK' for r in out['supervised']))
