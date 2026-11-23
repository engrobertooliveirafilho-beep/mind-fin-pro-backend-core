import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from app.runtime.p2614_real_fill_replay import replay

class CapitalReservation(unittest.TestCase):
 def test_no_overcommit(self):
  t=datetime(2026,1,1)
  candles=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  edges=[{'edge_id':str(i)} for i in range(3)]
  def fill(edge,candles,features,i,*cost):
   return {'signal_i':i,'entry_i':i+1,'exit_i':i+10,'r':0.,'real_execution_allowed':False}
  with patch.object(replay,'simulate_fill',fill):
   summary,curve,trades=replay.replay_portfolio('PAPER',edges,candles,{},risk_pct=.6)
  self.assertEqual(summary['real_execution_allowed'],False)
  self.assertEqual(summary['trades'],1)
