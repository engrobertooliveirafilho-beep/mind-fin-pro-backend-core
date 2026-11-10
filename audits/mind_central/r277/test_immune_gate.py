import math, unittest
from immunity import CognitiveImmuneSystem
from immune_gate import guarded_scan, InvalidCognitiveScore
class Spy(CognitiveImmuneSystem):
    def __init__(self): super().__init__(); self.calls=0
    def scan(self,p): self.calls+=1; return super().scan(p)
class Test(unittest.TestCase):
    def test_original_nan_bypass(self):
        r=CognitiveImmuneSystem().scan({'score':float('nan')})
        self.assertEqual(r['flags'],[])
        self.assertTrue(math.isnan(r['normalized_score']))
    def test_original_bool_bypass(self): self.assertEqual(CognitiveImmuneSystem().scan({'score':True})['flags'],[])
    def test_valid_zero(self): self.assertEqual(guarded_scan(Spy(),{'score':0})['normalized_score'],0)
    def test_valid_bounds(self):
        for v in [-1,1]: self.assertEqual(guarded_scan(Spy(),{'score':v})['normalized_score'],v)
    def reject(self,p):
        s=Spy()
        with self.assertRaises(InvalidCognitiveScore): guarded_scan(s,p)
        self.assertEqual(s.calls,0)
    def test_nan(self): self.reject({'score':float('nan')})
    def test_inf(self): self.reject({'score':float('inf')})
    def test_negative_inf(self): self.reject({'score':-float('inf')})
    def test_bool(self): self.reject({'score':True})
    def test_missing(self): self.reject({})
    def test_extra(self): self.reject({'score':0,'authorization':'REAL_ORDERS'})
    def test_out_of_bounds(self): self.reject({'score':1.1})
    def test_string(self): self.reject({'score':'0.5'})
    def test_huge_int(self): self.reject({'score':10**10000})
if __name__=='__main__': unittest.main()
