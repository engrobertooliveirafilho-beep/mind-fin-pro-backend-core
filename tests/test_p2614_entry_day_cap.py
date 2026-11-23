import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from app.runtime.p2614_real_fill_replay import replay

class EntryDayCap(unittest.TestCase):
 def test_signal_before_midnight_counts_on_entry_day(self):
  t=datetime(2026,1,1,23,0)
  candles=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  edges=[{'edge_id':'A'},{'edge_id':'B'}]
  def fill(edge,candles,features,i,*cost):
   if i not in (60,61): return None
   return {'signal_i':i,'entry_i':i+1,'exit_i':i+2,'r':0.,'real_execution_allowed':False}
  with patch.object(replay,'simulate_fill',fill):
   summary,curve,trades=replay.replay_portfolio('PAPER',edges,candles,{},max_trades_per_day=1)
  self.assertEqual(summary['trades'],1)
  self.assertEqual(trades[0]['entry_i'],61)
