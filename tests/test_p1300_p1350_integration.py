import unittest
from datetime import datetime,timedelta,timezone
from app.runtime.p1300_p1350_integration import run
def bars():
 t=datetime(2026,1,1,tzinfo=timezone.utc)
 return [{'timestamp':(t+timedelta(minutes=i)).isoformat(),'open':100+i,'high':100+i,'low':100+i,'close':100+i} for i in range(28)]
class Integration(unittest.TestCase):
 def test_train_only(self):
  result=run(bars(),train=20)
  self.assertEqual(result['regime_fit_scope'],'TRAIN_ONLY')
  self.assertEqual(result['regime_fit_bars'],20)
  self.assertEqual(result['p1350']['bars'],20)
 def test_future_mutation_no_leak(self):
  a=bars();b=bars();b[-1].update(open=500,high=500,low=500,close=500)
  self.assertEqual(run(a,train=20)['training_source_sha256'],run(b,train=20)['training_source_sha256'])
  self.assertNotEqual(run(a,train=20)['full_source_sha256'],run(b,train=20)['full_source_sha256'])
 def test_reject_insufficient_training(self):
  with self.assertRaises(ValueError):run(bars(),train=12)
 def test_fail_closed(self):
  result=run(bars(),train=20)
  self.assertFalse(result['order_send_allowed'])
  self.assertFalse(result['promotion_allowed'])
  self.assertFalse(result['historical_source_verified'])
 def test_reject_fake_historical_hash(self):
  with self.assertRaises(ValueError):run(bars(),train=20,historical_source_sha256='0'*64)
 def test_verified_hash(self):
  digest=run(bars(),train=20)['full_source_sha256']
  self.assertTrue(run(bars(),train=20,historical_source_sha256=digest)['historical_source_verified'])
