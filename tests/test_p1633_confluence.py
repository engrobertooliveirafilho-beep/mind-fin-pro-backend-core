import unittest,copy,json
from pathlib import Path
from app.runtime.p1633_confluence import reconcile,reconcile_file
P=Path(__file__).parent/'fixtures'/'p1633_confluence_patterns.json'
class TestP1633(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=json.loads(P.read_text()) if P.exists() else None
 def sample(self):
  return {'asset':'EURUSD','timeframe':'H1','specialist_id':'sample_1','family':'RSI','profile':'PAPER','deployment_score':50,'confluence_score':50,'opportunity_score':50,'pattern_status':'MINED_CANDIDATE','decision':'WATCH_ONLY'}
 def test_real(self):
  if self.rows is None:self.skipTest('historical fixture not published')
  self.assertEqual(reconcile_file(P)['candidates'],106)
 def test_watch(self):self.assertEqual(reconcile([self.sample()])['status'],'WATCH_ONLY')
 def test_no_orders(self):self.assertFalse(reconcile([self.sample()])['order_send_allowed'])
 def test_no_promotion(self):self.assertFalse(reconcile([self.sample()])['promotion_allowed'])
 def test_no_e2e(self):self.assertFalse(reconcile([self.sample()])['e2e_certified'])
 def test_duplicate(self):
  r=self.sample()
  with self.assertRaises(ValueError):reconcile([r,r])
 def test_promoted(self):
  r=self.sample();r['decision']='PROMOTE'
  with self.assertRaises(ValueError):reconcile([r])
 def test_nan(self):
  r=self.sample();r['opportunity_score']='NaN'
  with self.assertRaises(ValueError):reconcile([r])
 def test_overflow(self):
  r=self.sample();r['confluence_score']=101
  with self.assertRaises(ValueError):reconcile([r])
 def test_empty(self):
  with self.assertRaises(ValueError):reconcile([])
