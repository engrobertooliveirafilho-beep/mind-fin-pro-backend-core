import unittest
from datetime import datetime,timedelta
from app.runtime.p2614_real_fill_replay.replay import replay_portfolio

class CandleTimeGate(unittest.TestCase):
 def test_duplicate_timestamp_rejected(self):
  t=datetime(2026,1,1)
  c=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  c[50]['time']=c[49]['time']
  with self.assertRaisesRegex(ValueError,'NONMONOTONIC_CANDLE_TIME'):
   replay_portfolio('PAPER',[],c,{})
 def test_reverse_timestamp_rejected(self):
  t=datetime(2026,1,1)
  c=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  c[50]['time']=t
  with self.assertRaisesRegex(ValueError,'NONMONOTONIC_CANDLE_TIME'):
   replay_portfolio('PAPER',[],c,{})
 def test_valid_timestamps_accepted(self):
  t=datetime(2026,1,1)
  c=[{'time':t+timedelta(minutes=i)} for i in range(100)]
  summary,_,_=replay_portfolio('PAPER',[],c,{})
  self.assertFalse(summary['real_execution_allowed'])
