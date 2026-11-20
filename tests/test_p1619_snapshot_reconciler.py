import copy
import json
import unittest
from pathlib import Path
from app.runtime.p1619_snapshot_reconciler import reconcile, reconcile_file

class TestP1619(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).parent / 'fixtures' / 'p1619_candle_trigger_snapshot.json'
        cls.rows = json.loads(cls.path.read_text()) if cls.path.is_file() else None
    def test_historical_snapshot(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        result = reconcile_file(self.path)
        self.assertEqual(result['rows'], 181)
        self.assertEqual(result['status'], 'RECONCILED')
        self.assertEqual(result['mismatches'], [])
    def test_sha(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        self.assertEqual(reconcile_file(self.path)['historical_sha256'], 'cf900714c141ea1d6e9a8e9317de4a6e4658240414f99c6ec70e792c1b8c9067')
    def test_reject_score_mismatch(self):
        rows = [dict(asset='XAUUSD',timeframe='H1',candle_score=999,**{k:0 for k in ('doji','hammer','shooting_star','bullish_engulfing','bearish_engulfing','inside_bar','outside_bar')})]
        self.assertEqual(reconcile(rows)['status'], 'SCORE_MISMATCH')
    def test_reject_duplicate(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        with self.assertRaises(ValueError): reconcile(self.rows+[self.rows[0]])
    def test_reject_boolean_as_int(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        rows=copy.deepcopy(self.rows);rows[0]['doji']=True
        with self.assertRaises(ValueError): reconcile(rows)
    def test_reject_negative(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        rows=copy.deepcopy(self.rows);rows[0]['candle_score']=-1
        with self.assertRaises(ValueError): reconcile(rows)
    def test_reject_empty(self):
        with self.assertRaises(ValueError): reconcile([])
    def test_no_orders(self):
        if self.rows is None: self.skipTest('historical fixture not installed')
        result=reconcile(self.rows)
        self.assertFalse(result['order_send_allowed']);self.assertFalse(result['promotion_allowed']);self.assertFalse(result['e2e_certified'])
if __name__=='__main__': unittest.main()
