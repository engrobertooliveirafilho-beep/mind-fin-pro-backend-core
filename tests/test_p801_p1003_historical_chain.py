"""Offline integration regression with original Drive reports; never sends orders."""
import json,os,unittest
from pathlib import Path
from app.runtime.p801_release_interlock import release_gate
from app.runtime.p1001_master_interlock import gate
from app.runtime.p1002_health_reconciler import reconcile
from app.runtime.p1003_recovery_interlock import assess
from app.runtime.p1000_scheduler_gate import validate

@unittest.skipUnless(os.getenv('ELDORA_HISTORICAL_DIR'),'historical evidence directory required')
class HistoricalChain(unittest.TestCase):
 def test_blocked_chain(self):
  root=Path(os.environ['ELDORA_HISTORICAL_DIR'])
  read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
  release=release_gate(read('p601_700_allocation.json'),read('p601_700_master_report.json'),read('p701_supervised_edges.json'),read('p801_release_gate.json'))
  master=gate(read('master_daily_report.json'),release)
  health=reconcile(read('p1002_health_report.json'),master)
  recovery=assess(read('p1003_recovery_report.json'),master,{})
  scheduler=validate(read('p1000_scheduler_report.json'),read('latest_daily_run.json'),master)
  self.assertEqual(release['certification'],'BLOCKED_RISK')
  self.assertEqual({v[0] for v in release['risk_audit']['violations']},{'asset','timeframe','family'})
  self.assertEqual(len(release['risk_audit']['violations']),3)
  self.assertEqual(master['certification'],'BLOCKED_UPSTREAM')
  self.assertEqual(health['HEALTH'],'RED')
  self.assertFalse(recovery['automatic_rerun_allowed'])
  self.assertFalse(scheduler['scheduler_activation_allowed'])
  self.assertFalse(master['order_send_allowed'])
if __name__=='__main__':unittest.main()
