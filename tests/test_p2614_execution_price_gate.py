import unittest
from datetime import datetime,timedelta
from app.runtime.p2614_real_fill_replay.execution import simulate_fill

class ExecutionPriceGate(unittest.TestCase):
 def setUp(self):
  t=datetime(2026,1,1)
  self.c=[{'time':t+timedelta(minutes=i),'open':100.,'close':100.5} for i in range(30)]
  self.e={'family':'TREND','direction':'BUY_PAPER'}
  self.ft={'session':'US_AFTERNOON','trend':'TREND_UP','regime':'LOW_VOL','wick_ratio':.5,'body_ratio':.5,'atr':1.,'atr_med':1.}
 def test_zero_entry(self):
  self.c[2]['open']=0
  self.assertIsNone(simulate_fill(self.e,self.c,{1:self.ft},1))
 def test_nan_exit(self):
  self.c[14]['close']=float('nan')
  self.assertIsNone(simulate_fill(self.e,self.c,{1:self.ft},1))
 def test_negative_exit(self):
  self.c[14]['close']=-2
  self.assertIsNone(simulate_fill(self.e,self.c,{1:self.ft},1))
 def test_valid(self):
  self.assertFalse(simulate_fill(self.e,self.c,{1:self.ft},1)['real_execution_allowed'])
