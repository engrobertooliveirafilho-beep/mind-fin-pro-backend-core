import unittest
from mind_trader.research.et665_r443_cluster_gate import validate_cluster
class TestClusterGate(unittest.TestCase):
    def setUp(self):
        self.c={'decision':'PROMOTE_CLUSTER'}
        self.m=[{'candidate_id':'a','empirical_certified':True,'trade_series_sha256':'aa'}, {'candidate_id':'b','empirical_certified':True,'trade_series_sha256':'bb'}]
        self.e={'mode':'PAPER_ONLY','real_execution_allowed':False,'source_type':'EMPIRICAL_TRADES','independent_validation':True}
    def test_fixture(self): self.assertEqual(validate_cluster(self.c,self.m,self.e),(True,'RESEARCH_ELIGIBLE_ONLY'))
    def test_single_member(self): self.assertFalse(validate_cluster(self.c,self.m[:1],self.e)[0])
    def test_duplicate(self): self.assertFalse(validate_cluster(self.c,[self.m[0]]*2,self.e)[0])
    def test_synthetic(self): self.assertFalse(validate_cluster(self.c,self.m,{**self.e,'source_type':'SYNTHETIC'})[0])
    def test_no_validation(self): self.assertFalse(validate_cluster(self.c,self.m,{**self.e,'independent_validation':False})[0])
    def test_live(self): self.assertFalse(validate_cluster(self.c,self.m,{**self.e,'mode':'LIVE'})[0])
    def test_orders(self): self.assertFalse(validate_cluster(self.c,self.m,{**self.e,'real_execution_allowed':True})[0])
    def test_unverified(self): self.assertFalse(validate_cluster(self.c,[{**self.m[0],'empirical_certified':False},self.m[1]],self.e)[0])
    def test_missing_hash(self): self.assertFalse(validate_cluster(self.c,[{**self.m[0],'trade_series_sha256':''},self.m[1]],self.e)[0])
    def test_not_promoted(self): self.assertFalse(validate_cluster({'decision':'OBSERVE'},self.m,self.e)[0])
if __name__=='__main__': unittest.main()
