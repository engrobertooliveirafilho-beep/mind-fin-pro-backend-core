import unittest
from datetime import datetime,timedelta,timezone
from app.runtime.p1350_regime_classifier import classify
def bars(closes):
 t=datetime(2026,1,1,tzinfo=timezone.utc)
 return [{'timestamp':(t+timedelta(minutes=i)).isoformat(),'open':x,'high':x,'low':x,'close':x} for i,x in enumerate(closes)]
class TestRegime(unittest.TestCase):
 def test_range(self):self.assertEqual(classify(bars([100]*20))['regime'],'RANGE')
 def test_up(self):self.assertEqual(classify(bars([100+i for i in range(20)]))['regime'],'TREND_UP')
 def test_down(self):self.assertEqual(classify(bars([100-i for i in range(20)]))['regime'],'TREND_DOWN')
 def test_vol(self):self.assertEqual(classify(bars([100,120]*10))['regime'],'HIGH_VOLATILITY')
 def test_insufficient(self):
  with self.assertRaises(ValueError):classify(bars([100]*3))
 def test_duplicate_timestamp(self):
  data=bars([100]*20);data[2]['timestamp']=data[1]['timestamp']
  with self.assertRaises(ValueError):classify(data)
 def test_future_reordered(self):
  data=bars([100]*20);data[1],data[2]=data[2],data[1]
  with self.assertRaises(ValueError):classify(data)
 def test_invalid_price(self):
  data=bars([100]*20);data[3]['close']=-1
  with self.assertRaises(ValueError):classify(data)
 def test_nan(self):
  data=bars([100]*20);data[3]['close']='NaN'
  with self.assertRaises(ValueError):classify(data)
 def test_no_order(self):self.assertFalse(classify(bars([100]*20))['order_send_allowed'])
 def test_determinism(self):self.assertEqual(classify(bars([100]*20))['source_sha256'],classify(bars([100]*20))['source_sha256'])
 def test_no_oos_claim(self):self.assertFalse(classify(bars([100]*20))['validated_out_of_sample'])
