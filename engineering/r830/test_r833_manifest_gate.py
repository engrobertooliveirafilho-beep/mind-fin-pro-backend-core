import unittest
from copy import deepcopy
from r833_manifest_gate import BUCKETS,reconcile
class Tests(unittest.TestCase):
 def setUp(self):
  self.data={'buckets':{b:['app.'+b.lower()] for b in BUCKETS},'counts':{b:1 for b in BUCKETS},'policy':{'delete_files':False,'orphaned_modules_policy':'do_not_integrate_without_explicit_revalidation'}}
 def test_valid(self): self.assertTrue(reconcile(self.data)['valid'])
 def test_no_promotion(self): self.assertFalse(reconcile(self.data)['orphan_promotion_allowed'])
 def test_duplicate(self):
  x=deepcopy(self.data);x['buckets'][BUCKETS[1]]=x['buckets'][BUCKETS[0]];self.assertFalse(reconcile(x)['valid'])
 def test_count_mismatch(self):
  x=deepcopy(self.data);x['counts'][BUCKETS[0]]=2;self.assertFalse(reconcile(x)['valid'])
 def test_delete_policy(self):
  x=deepcopy(self.data);x['policy']['delete_files']=True;self.assertFalse(reconcile(x)['valid'])
 def test_orphan_policy(self):
  x=deepcopy(self.data);x['policy']['orphaned_modules_policy']='promote';self.assertFalse(reconcile(x)['valid'])
 def test_missing_bucket(self):
  x=deepcopy(self.data);del x['buckets'][BUCKETS[0]];self.assertFalse(reconcile(x)['valid'])
 def test_bad_module(self):
  x=deepcopy(self.data);x['buckets'][BUCKETS[0]]=['unknown'];self.assertFalse(reconcile(x)['valid'])
 def test_bad_json(self): self.assertFalse(reconcile('{')['valid'])
if __name__=='__main__':unittest.main()
