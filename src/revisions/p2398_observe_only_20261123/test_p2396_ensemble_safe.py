import unittest
from p2396_ensemble_safe import build_ensemble
ROW = {'allowed':False,'route':'OBSERVE_ONLY','source_edge':'P2391_8149352397','mode':'PAPER_ONLY','real_orders':'FORBIDDEN','ftmo_real':'FORBIDDEN'}
class EnsembleTests(unittest.TestCase):
    def test_original_observe(self):
        r=build_ensemble([ROW]).vote()
        self.assertEqual((r.vote,r.operational_members,r.allowed),('OBSERVE_ONLY',0,False))
    def test_duplicate_source(self):
        self.assertEqual(build_ensemble([ROW,dict(ROW)]).vote().reason,'MISSING_OR_DUPLICATE_SOURCE')
    def test_distinct_observers_not_operational(self):
        r=build_ensemble([ROW,{**ROW,'source_edge':'OTHER'}]).vote()
        self.assertFalse(r.allowed)
        self.assertEqual(r.vote,'OBSERVE_ONLY')
    def test_unsafe_member(self):
        self.assertEqual(build_ensemble([{**ROW,'mode':'LIVE'}]).vote().vote,'BLOCK')
    def test_forged_promotion(self):
        self.assertEqual(build_ensemble([{**ROW,'allowed':True,'route':'PAPER_SIGNAL_CANDIDATE'}]).vote().vote,'BLOCK')
    def test_bad_quorum(self):
        self.assertEqual(build_ensemble([ROW],quorum=True).vote().vote,'BLOCK')
    def test_invalid_row(self):
        self.assertEqual(build_ensemble([None]).vote().vote,'BLOCK')
if __name__=='__main__': unittest.main()
