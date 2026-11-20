import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from app.runtime.p501_decision_gate import classify,run,BLOCKS

def row(score=3.1,**kw):
    r=dict(edge_id='a',shadow_score=score,execution_mode='SHADOW_ONLY',order_sent=False,**BLOCKS)
    r.update(kw)
    return r

class TestGate(unittest.TestCase):
    def test_high(self):self.assertEqual(classify([row()])[0]['decision'],'HIGH_PRIORITY_DEMO')
    def test_candidate(self):self.assertEqual(classify([row(2.1)])[0]['decision'],'DEMO_CANDIDATE')
    def test_watch(self):self.assertEqual(classify([row(1.1)])[0]['decision'],'WATCHLIST')
    def test_boundary_high(self):self.assertEqual(classify([row(3)])[0]['decision'],'HIGH_PRIORITY_DEMO')
    def test_boundary_candidate(self):self.assertEqual(classify([row(2)])[0]['decision'],'DEMO_CANDIDATE')
    def test_missing(self):
        with self.assertRaises(ValueError):classify([])
    def test_nan(self):
        with self.assertRaises(ValueError):classify([row(float('nan'))])
    def test_inf(self):
        with self.assertRaises(ValueError):classify([row(float('inf'))])
    def test_bool(self):
        with self.assertRaises(ValueError):classify([row(True)])
    def test_duplicate(self):
        with self.assertRaises(ValueError):classify([row(),row()])
    def test_real(self):
        with self.assertRaises(ValueError):classify([row(REAL_ORDERS='ENABLED')])
    def test_nonshadow(self):
        with self.assertRaises(ValueError):classify([row(execution_mode='DEMO')])
    def test_sent(self):
        with self.assertRaises(ValueError):classify([row(order_sent=True)])
    def test_no_close(self):self.assertFalse(classify([row()])[0]['position_close_sent'])
    def test_write(self):
        with TemporaryDirectory() as d:
            p=Path(d)
            (p/'in.json').write_text(json.dumps([row()]))
            result=run(p/'in.json',p/'out')
            self.assertFalse(result['ORDER_SENT'])
            self.assertTrue((p/'out/p501_shadow_decisions.json').exists())
