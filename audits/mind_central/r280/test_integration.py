import unittest, math
from immunity import CognitiveImmuneSystem
from immune_gate import guarded_scan, InvalidCognitiveScore
class Spy(CognitiveImmuneSystem):
    def __init__(self):super().__init__();self.calls=0
    def scan(self,p):self.calls+=1;return super().scan(p)
class Tests(unittest.TestCase):
    def reject(self,p):
        s=Spy()
        with self.assertRaises(InvalidCognitiveScore):guarded_scan(s,p)
        self.assertEqual(s.calls,0)
    def test_valid(self):
        s=Spy();self.assertEqual(guarded_scan(s,{'score':0.5})['normalized_score'],0.5);self.assertEqual(s.calls,1)
    def test_negative_bound(self):self.assertEqual(guarded_scan(Spy(),{'score':-1})['normalized_score'],-1)
    def test_positive_bound(self):self.assertEqual(guarded_scan(Spy(),{'score':1})['normalized_score'],1)
    def test_nan(self):self.reject({'score':float('nan')})
    def test_inf(self):self.reject({'score':float('inf')})
    def test_negative_inf(self):self.reject({'score':-float('inf')})
    def test_bool(self):self.reject({'score':True})
    def test_missing(self):self.reject({})
    def test_extra(self):self.reject({'score':0,'authorization':'REAL_ORDERS'})
    def test_out_of_range(self):self.reject({'score':2})
    def test_string(self):self.reject({'score':'0.5'})
    def test_large_int(self):self.reject({'score':10**10000})
    def test_original_nan_bypass(self):
        r=CognitiveImmuneSystem().scan({'score':float('nan')});self.assertFalse(r['flags']);self.assertTrue(math.isnan(r['normalized_score']))
if __name__=='__main__':unittest.main()
