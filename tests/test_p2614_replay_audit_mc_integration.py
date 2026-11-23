import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from app.runtime.p2614_real_fill_replay import replay
from app.runtime.p2614_real_fill_replay.audit import audit_trades
from app.runtime.p2614_real_fill_replay.montecarlo import monte_carlo_from_trades

class ReplayAuditMonteCarloIntegration(unittest.TestCase):
 def test_paper_pipeline(self):
  t=datetime(2026,1,1)
  candles=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  edges=[{'edge_id':'A','risk_model':'ATR_STOP'}]
  def fill(edge,candles,features,i,*cost):
   return {'signal_i':i,'entry_i':i+1,'exit_i':i+3,'r':0.5,'real_execution_allowed':False}
  with patch.object(replay,'simulate_fill',fill):
   summary,curve,trades=replay.replay_portfolio('PAPER',edges,candles,{},risk_pct=.01)
  self.assertGreater(len(trades),0)
  self.assertFalse(summary['real_execution_allowed'])
  self.assertTrue(audit_trades(trades)['passed'],audit_trades(trades)['errors'])
  result=monte_carlo_from_trades(trades,runs=20)
  self.assertEqual(result['runs'],20)
  self.assertEqual(result['method'],'bootstrap_with_replacement')
