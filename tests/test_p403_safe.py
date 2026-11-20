import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from app.runtime.p403_safe import BLOCKS,score_routes,run

def route(**kw):
    r=dict(edge_id='e1',score=2.0,timeframe='M15',family='RSI_REVERSION',order_sent=False,**BLOCKS);r.update(kw);return r

def evidence(**kw):
    e=dict(POSITIONS_TOTAL=0,**BLOCKS);e.update(kw);return e

class Regression(unittest.TestCase):
    def test_score(self):self.assertEqual(score_routes([route()],evidence())[0]['shadow_score'],2.05)
    def test_shadow_only(self):self.assertEqual(score_routes([route()],evidence())[0]['execution_mode'],'SHADOW_ONLY')
    def test_order_false(self):self.assertFalse(score_routes([route()],evidence())[0]['order_sent'])
    def test_missing_routes(self):
        with self.assertRaises(ValueError):score_routes([],evidence())
    def test_missing_evidence(self):
        with self.assertRaises(ValueError):score_routes([route()],{})
    def test_nan(self):
        with self.assertRaises(ValueError):score_routes([route(score=float('nan'))],evidence())
    def test_inf(self):
        with self.assertRaises(ValueError):score_routes([route(score=float('inf'))],evidence())
    def test_duplicate(self):
        with self.assertRaises(ValueError):score_routes([route(),route()],evidence())
    def test_real_orders(self):
        with self.assertRaises(ValueError):score_routes([route(REAL_ORDERS='ALLOWED')],evidence())
    def test_evidence_real(self):
        with self.assertRaises(ValueError):score_routes([route()],evidence(FTMO_REAL='ALLOWED'))
    def test_evidence_live_rejected(self):
        with self.assertRaises(ValueError):score_routes([route()],evidence(LIVE='ALLOWED'))
    def test_order_sent(self):
        with self.assertRaises(ValueError):score_routes([route(order_sent=True)],evidence())
    def test_invalid_positions(self):
        with self.assertRaises(ValueError):score_routes([route()],evidence(POSITIONS_TOTAL=-1))
    def test_deterministic_ranking(self):
        self.assertEqual([r['edge_id'] for r in score_routes([route(edge_id='b'),route(edge_id='a')],evidence())],['a','b'])
    def test_shadow_files(self):
        with TemporaryDirectory() as d:
            p=Path(d);(p/'routes.json').write_text(json.dumps([route()]));(p/'evidence.json').write_text(json.dumps(evidence()))
            self.assertFalse(run(p/'routes.json',p/'evidence.json',p/'out')['ORDER_SENT'])
            self.assertEqual(len(json.loads((p/'out/p404_shadow_signal_ranked.json').read_text())),1)
    def test_missing_file_no_output(self):
        with TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaises(FileNotFoundError):run(p/'absent',p/'absent2',p/'out')
            self.assertFalse((p/'out').exists())
