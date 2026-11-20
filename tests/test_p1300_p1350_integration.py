import unittest
from datetime import datetime,timedelta,timezone
from app.runtime.p1300_p1350_integration import run
def bars():
 t=datetime(2026,1,1,tzinfo=timezone.utc)
 return [{'timestamp':(t+timedelta(minutes=i)).isoformat(),'open':100+i,'high':100+i,'low':100+i,'close':100+i} for i in range(20)]
class Integration(unittest.TestCase):
 def test_same_source(self):
  result=run(bars())
  self.assertEqual(result['p1300']['source_sha256'],result['p1350']['source_sha256'])
 def test_fail_closed(self):
  result=run(bars())
  self.assertFalse(result['order_send_allowed'])
  self.assertFalse(result['promotion_allowed'])
  self.assertFalse(result['historical_source_verified'])
 def test_reject_fake_historical_hash(self):
  with self.assertRaises(ValueError):run(bars(),historical_source_sha256='0'*64)
 def test_verified_hash(self):
  digest=run(bars())['p1300']['source_sha256']
  self.assertTrue(run(bars(),historical_source_sha256=digest)['historical_source_verified'])
 def test_no_lookahead(self):
  first=bars();second=bars();second[0]['open']=99;second[0]['low']=99;second[0]['close']=99
  self.assertEqual(run(first)['p1300']['test_net_return'],run(second)['p1300']['test_net_return'])
