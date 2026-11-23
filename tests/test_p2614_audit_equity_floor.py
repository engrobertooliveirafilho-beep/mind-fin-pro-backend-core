import unittest
from app.runtime.p2614_real_fill_replay.audit import audit_trades

class EquityFloorAudit(unittest.TestCase):
 def test_floor_matches_replay(self):
  trade={'signal_i':0,'entry_i':1,'exit_i':2,'edge_id':'A','capital_before':1.0,'capital_after':0.01,'pnl_usd':-2.0,'r':-2.0,'real_execution_allowed':False}
  result=audit_trades([trade])
  self.assertTrue(result['passed'],result['errors'])
 def test_unexplained_equity_rejected(self):
  trade={'signal_i':0,'entry_i':1,'exit_i':2,'edge_id':'A','capital_before':1.0,'capital_after':0.5,'pnl_usd':-2.0,'r':-2.0,'real_execution_allowed':False}
  result=audit_trades([trade])
  self.assertFalse(result['passed'])
  self.assertTrue(any('PNL_EQUITY_MISMATCH' in e for e in result['errors']))
