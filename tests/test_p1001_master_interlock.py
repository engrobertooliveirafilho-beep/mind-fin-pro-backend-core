import json,os,unittest
from pathlib import Path
from app.runtime.p1001_master_interlock import gate
MASTER={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN','ORDER_SEND_ALLOWED':False,'ALLOCATED_EDGES':4,'SUPERVISED_EDGES':4,'POSITIONS_TOTAL':0,'EQUITY':100001.49,'HEALTH':'GREEN'}
DECISION={'certification':'BLOCKED_RISK','real_ftmo_release_allowed':False,'order_sent':False}
class Tests(unittest.TestCase):
 def test_safe(self):
  r=gate(MASTER,DECISION);self.assertEqual(r['health'],'RED');self.assertFalse(r['e2e_certified'])
 def test_orders(self):
  with self.assertRaises(ValueError):gate({**MASTER,'ORDER_SEND_ALLOWED':True},DECISION)
 def test_live(self):
  with self.assertRaises(ValueError):gate({**MASTER,'REAL_ORDERS':'ALLOWED'},DECISION)
 def test_positions(self):
  with self.assertRaises(ValueError):gate({**MASTER,'POSITIONS_TOTAL':1},DECISION)
 def test_mismatch(self):
  with self.assertRaises(ValueError):gate({**MASTER,'SUPERVISED_EDGES':3},DECISION)
 def test_nan(self):
  with self.assertRaises(ValueError):gate({**MASTER,'EQUITY':'NaN'},DECISION)
 def test_upstream(self):
  with self.assertRaises(ValueError):gate(MASTER,{**DECISION,'order_sent':True})
 def test_missing(self):
  with self.assertRaises(ValueError):gate({},DECISION)
 @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical report not mounted')
 def test_original_report(self):
  original=json.loads((Path(os.environ['ELDORA_HISTORICAL_DIR'])/'master_daily_report.json').read_text())
  self.assertEqual(gate(original,DECISION)['certification'],'BLOCKED_UPSTREAM')
