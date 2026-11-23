import unittest
from datetime import datetime,timedelta
from app.runtime.p2614_real_fill_replay.execution import simulate_fill

class FeatureVectorGate(unittest.TestCase):
 def setUp(self):
  t=datetime(2026,1,1)
  self.c=[{'time':t+timedelta(minutes=i),'open':100.,'high':101.,'low':99.,'close':100.5} for i in range(30)]
  self.e={'family':'TREND','direction':'BUY_PAPER'}
  self.ft={'session':'US_AFTERNOON','trend':'TREND_UP','regime':'LOW_VOL','wick_ratio':.5,'body_ratio':.5,'atr':1.,'atr_med':1.}
 def test_missing_feature_rejected(self):
  x=dict(self.ft);del x['atr']
  self.assertIsNone(simulate_fill(self.e,self.c,{1:x},1))
 def test_nonfinite_feature_rejected(self):
  x=dict(self.ft,atr=float('nan'))
  self.assertIsNone(simulate_fill(self.e,self.c,{1:x},1))
 def test_zero_atr_rejected(self):
  x=dict(self.ft,atr=0.)
  self.assertIsNone(simulate_fill(self.e,self.c,{1:x},1))
 def test_valid_paper_preserved(self):
  x=simulate_fill(self.e,self.c,{1:self.ft},1)
  self.assertIsNotNone(x)
  self.assertIs(x['real_execution_allowed'],False)
