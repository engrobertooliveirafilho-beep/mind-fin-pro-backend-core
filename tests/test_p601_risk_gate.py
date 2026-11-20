import os
import unittest
from pathlib import Path
from app.runtime.p601_risk_gate import audit,run,BLOCKS

def row(**kw):
    r=dict(edge_id='x',asset='A',timeframe='H1',family='F',risk_pct=.001,allocation_status='ALLOCATED_SIMULATED',order_sent=False,**BLOCKS);r.update(kw);return r

def report(**kw):
    r=dict(TOTAL_ALLOCATED_RISK_PCT=.001,ORDER_SENT=False,**BLOCKS);r.update(kw);return r

class TestRiskGate(unittest.TestCase):
    @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical Drive exports not mounted')
    def test_historical_rejected(self):
        root=Path(os.environ['ELDORA_HISTORICAL_DIR'])
        self.assertEqual(run(root/'p601_700_allocation.json',root/'p601_700_master_report.json')['status'],'REJECTED_CAP')
    def test_clean(self):self.assertEqual(audit([row()],report())['status'],'PASS')
    def test_over_cap(self):self.assertEqual(audit([row(risk_pct=.006)],report(TOTAL_ALLOCATED_RISK_PCT=.006))['status'],'REJECTED_CAP')
    def test_duplicate(self):
        with self.assertRaises(ValueError):audit([row(),row()],report(TOTAL_ALLOCATED_RISK_PCT=.002))
    def test_nan(self):
        with self.assertRaises(ValueError):audit([row(risk_pct=float('nan'))],report())
    def test_negative(self):
        with self.assertRaises(ValueError):audit([row(risk_pct=-.001)],report(TOTAL_ALLOCATED_RISK_PCT=-.001))
    def test_real(self):
        with self.assertRaises(ValueError):audit([row(REAL_ORDERS='YES')],report())
    def test_report_real(self):
        with self.assertRaises(ValueError):audit([row()],report(REAL_ORDERS='YES'))
    def test_mismatch(self):
        with self.assertRaises(ValueError):audit([row()],report(TOTAL_ALLOCATED_RISK_PCT=.002))
    def test_blocked_nonzero(self):
        with self.assertRaises(ValueError):audit([row(allocation_status='BLOCKED_BY_CAP')],report())
    def test_missing(self):
        with self.assertRaises(ValueError):audit([],report())
    def test_order(self):
        with self.assertRaises(ValueError):audit([row(order_sent=True)],report())
