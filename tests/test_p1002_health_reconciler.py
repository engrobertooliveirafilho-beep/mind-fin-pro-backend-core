import unittest,json,os
from pathlib import Path
from app.runtime.p1002_health_reconciler import reconcile
U={'e2e_certified':False,'order_send_allowed':False,'certification':'BLOCKED_UPSTREAM'}
R={'REAL_ORDERS':'FORBIDDEN','FTMO_REAL':'FORBIDDEN','MT5_REAL':'FORBIDDEN','DISK_FREE_GB':39.85,'LOGS_TOTAL':6,'LATEST_LOG':'daily_run.log','HEALTH':'GREEN'}
class Tests(unittest.TestCase):
 def test_reconciled(self):self.assertEqual(reconcile(R,U)['HEALTH'],'RED')
 def test_no_e2e(self):self.assertFalse(reconcile(R,U)['E2E_CERTIFIED'])
 def test_no_orders(self):self.assertFalse(reconcile(R,U)['ORDER_SEND_ALLOWED'])
 def test_nan(self):
  with self.assertRaises(ValueError):reconcile({**R,'DISK_FREE_GB':float('nan')},U)
 def test_negative(self):
  with self.assertRaises(ValueError):reconcile({**R,'DISK_FREE_GB':-1},U)
 def test_missing_log(self):
  with self.assertRaises(ValueError):reconcile({**R,'LATEST_LOG':None},U)
 def test_real_orders(self):
  with self.assertRaises(ValueError):reconcile({**R,'REAL_ORDERS':'ALLOWED'},U)
 def test_upstream(self):
  with self.assertRaises(ValueError):reconcile(R,{**U,'e2e_certified':True})
 @unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical Drive export not mounted')
 def test_historical(self):
  r=json.loads((Path(os.environ['ELDORA_HISTORICAL_DIR'])/'p1002_health_report.json').read_text())
  self.assertEqual(reconcile(r,U)['HEALTH'],'RED')
