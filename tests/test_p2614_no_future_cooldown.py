import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from app.runtime.p2614_real_fill_replay import replay

class NoFutureCooldown(unittest.TestCase):
 def test_loss_cooldown_only_after_exit(self):
  t=datetime(2026,1,1)
  candles=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  edges=[{'edge_id':'edge','risk_model':'COOLDOWN'}]
  calls=[]
  def fill(edge,candles,features,i,*cost):
   calls.append(i)
   return {'signal_i':i,'entry_i':i+1,'exit_i':i+5,'r':-1.,'real_execution_allowed':False}
  with patch.object(replay,'simulate_fill',fill):
   summary,curve,trades=replay.replay_portfolio('PAPER',edges,candles,{})
  self.assertIn(60,calls, 'first signal must be evaluated')
  self.assertNotIn(65,calls, 'cooldown must begin at settlement')
  self.assertNotIn(66,calls)
  self.assertNotIn(67,calls)
  self.assertIn(68,calls, 'cooldown must expire after three settled bars')
  self.assertFalse(summary['real_execution_allowed'])
