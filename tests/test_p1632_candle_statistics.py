import unittest
from app.runtime.p1632_candle_statistics import summarize
FLAGS=('doji','hammer','shooting_star','bullish_engulfing','bearish_engulfing','inside_bar','outside_bar')
def row(**kw):
 r={'asset':'EURUSD','timeframe':'H1','candle_score':0,**{k:0 for k in FLAGS}}
 r.update(kw)
 return r
class TestP1632(unittest.TestCase):
 def test_empty(self):
  with self.assertRaises(ValueError):summarize([])
 def test_counts(self):
  result=summarize([row(hammer=1,candle_score=15),row(asset='XAUUSD',inside_bar=1,candle_score=10)])
  self.assertEqual(result['pattern_counts']['hammer'],1)
  self.assertEqual(result['timeframe_counts']['H1'],2)
  self.assertEqual(result['nonzero_scores'],2)
 def test_reject_fabricated_score(self):
  with self.assertRaises(ValueError):summarize([row(hammer=1,candle_score=0)])
 def test_no_winrate(self):
  self.assertIsNone(summarize([row()])['win_rate'])
 def test_no_orders(self):
  self.assertFalse(summarize([row()])['order_send_allowed'])
 def test_no_promotion(self):
  self.assertFalse(summarize([row()])['promotion_allowed'])
