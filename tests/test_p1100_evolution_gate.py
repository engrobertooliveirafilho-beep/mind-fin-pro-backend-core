import unittest,json,os
from pathlib import Path
from app.runtime.p1100_evolution_gate import audit
R={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN','ORDER_SENT':False}
class Tests(unittest.TestCase):
 def test_unsafe(self):
  with self.assertRaises(ValueError):audit({**R,'REAL_ORDERS':'ALLOWED'},[],[],{'status':'PASS'})
 def test_unknown_risk(self):
  with self.assertRaises(ValueError):audit(R,[],[],{'status':'UNKNOWN'})
 def test_unsafe_keep(self):
  a=audit(R,[],[{**R,'action':'KEEP','edge_id':'x'}],{'status':'REJECTED_CAP'});self.assertEqual(a['unsafe_keep'],['x'])
 def test_no_certification(self):self.assertFalse(audit(R,[],[],{'status':'PASS'})['e2e_certified'])
 @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'Drive original not mounted')
 def test_original_regimes(self):
  p=Path(os.environ['ELDORA_HISTORICAL_DIR']);data=json.loads((p/'p1350_regime_detection_engine.json').read_text())
  a=audit(R,data,[],{'status':'REJECTED_CAP'});self.assertEqual(len(a['unvalidated_regimes']),7)
 @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'Drive original not mounted')
 def test_original_decay(self):
  p=Path(os.environ['ELDORA_HISTORICAL_DIR']);data=json.loads((p/'p1450_edge_decay_monitor.json').read_text())
  self.assertFalse(audit(R,[],data,{'status':'REJECTED_CAP'})['order_send_allowed'])
