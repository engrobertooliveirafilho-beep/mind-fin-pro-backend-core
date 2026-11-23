import unittest
from datetime import datetime,timedelta
from unittest.mock import patch
from app.runtime.p2614_real_fill_replay import replay

class ReplayGuards(unittest.TestCase):
 def setUp(self):
  t=datetime(2026,1,1)
  self.c=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  self.edges=[{'edge_id':'A','direction':'BUY_PAPER','family':'MOMENTUM'}]
 def test_nan_fill_rejected(self):
  with patch.object(replay,'simulate_fill',lambda *a:{'signal_i':60,'entry_i':61,'exit_i':65,'r':float('nan'),'real_execution_allowed':False}):
   with self.assertRaisesRegex(ValueError,'INVALID_PAPER_FILL'):
    replay.replay_portfolio('test',self.edges,self.c,{})
 def test_live_fill_rejected(self):
  with patch.object(replay,'simulate_fill',lambda *a:{'signal_i':60,'entry_i':61,'exit_i':65,'r':1.,'real_execution_allowed':True}):
   with self.assertRaisesRegex(ValueError,'INVALID_PAPER_FILL'):
    replay.replay_portfolio('test',self.edges,self.c,{})
 def test_same_bar_entry_rejected(self):
  with patch.object(replay,'simulate_fill',lambda *a:{'signal_i':60,'entry_i':60,'exit_i':65,'r':1.,'real_execution_allowed':False}):
   with self.assertRaisesRegex(ValueError,'INVALID_EVENT_CHRONOLOGY'):
    replay.replay_portfolio('test',self.edges,self.c,{})
 def test_exit_outside_history_rejected(self):
  with patch.object(replay,'simulate_fill',lambda *a:{'signal_i':60,'entry_i':61,'exit_i':100,'r':1.,'real_execution_allowed':False}):
   with self.assertRaisesRegex(ValueError,'INVALID_EVENT_CHRONOLOGY'):
    replay.replay_portfolio('test',self.edges,self.c,{})
