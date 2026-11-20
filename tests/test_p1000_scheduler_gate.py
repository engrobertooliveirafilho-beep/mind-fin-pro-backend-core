import unittest,json,os
from pathlib import Path
from app.runtime.p1000_scheduler_gate import validate
class Tests(unittest.TestCase):
 def setUp(self):
  self.r={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN','ORDER_SEND_ALLOWED':False,'MODE':'DAILY_AUTONOMOUS_RESEARCH_AND_DEMO_EVIDENCE'}
  self.d={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN','ORDER_SEND_ALLOWED':False,'TIMESTAMP':'20260615_163616'}
  self.u={'e2e_certified':False,'order_send_allowed':False}
 def test_safe(self):self.assertEqual(validate(self.r,self.d,self.u)['status'],'BLOCKED_UPSTREAM')
 def test_no_activation(self):self.assertFalse(validate(self.r,self.d,self.u)['scheduler_activation_allowed'])
 def test_live(self):
  with self.assertRaises(ValueError):validate({**self.r,'REAL_ORDERS':'ALLOWED'},self.d,self.u)
 def test_mode(self):
  with self.assertRaises(ValueError):validate({**self.r,'MODE':'LIVE'},self.d,self.u)
 def test_upstream(self):
  with self.assertRaises(ValueError):validate(self.r,self.d,{**self.u,'e2e_certified':True})
 def test_run(self):
  with self.assertRaises(ValueError):validate(self.r,{**self.d,'ORDER_SEND_ALLOWED':True},self.u)
 @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'original Drive reports not mounted')
 def test_original(self):
  root=Path(os.environ['ELDORA_HISTORICAL_DIR'])
  self.assertEqual(validate(json.loads((root/'p1000_scheduler_report.json').read_text()),json.loads((root/'latest_daily_run.json').read_text()),self.u)['status'],'BLOCKED_UPSTREAM')
