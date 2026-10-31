import unittest
from strict_replay_guard import guarded_replay
H='a'*64
K=dict(expected_sha256=H,train_end='2026-01-01T00:00:00Z',test_start='2026-01-02T00:00:00Z',test_end='2026-01-03T00:00:00Z')
class TestGuard(unittest.TestCase):
 def run_guard(self,f,**k): return guarded_replay(f,'data.csv',**(K|k))
 def test_valid_paper(self):
  self.assertEqual(self.run_guard(lambda *a,**kw:dict(status='PAPER_REPLAY_ONLY',signals=3,mean_forward_return=.1,promotion_authorized=False,ftmo_certified=False))['status'],'PAPER_REPLAY_ONLY')
 def test_missing_hash(self): self.assertEqual(self.run_guard(lambda *a,**kw:None,expected_sha256='x')['status'],'BLOCKED')
 def test_exception(self):
  def bad(*a,**kw): raise ValueError('bad csv')
  self.assertEqual(self.run_guard(bad)['reason'],'ValueError')
 def test_empty(self): self.assertEqual(self.run_guard(lambda *a,**kw:dict(status='PAPER_REPLAY_ONLY',signals=0,mean_forward_return=None,promotion_authorized=False,ftmo_certified=False))['status'],'BLOCKED')
 def test_nonfinite(self): self.assertEqual(self.run_guard(lambda *a,**kw:dict(status='PAPER_REPLAY_ONLY',signals=1,mean_forward_return=float('nan'),promotion_authorized=False,ftmo_certified=False))['status'],'BLOCKED')
 def test_forged_promotion(self): self.assertEqual(self.run_guard(lambda *a,**kw:dict(status='CERTIFIED',signals=1,mean_forward_return=.1,promotion_authorized=True,ftmo_certified=True))['status'],'BLOCKED')
if __name__=='__main__': unittest.main()
