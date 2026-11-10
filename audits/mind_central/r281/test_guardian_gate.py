import unittest
from guardian_gate import checked_scan,GuardianRejected
class Guardian:
 def __init__(self):self.calls=0
 def scan(self):self.calls+=1;return {'protection_score':1.0}
BASE={'explanation':{'tags':[]},'reality':{'certainty':.5},'coherence':{'alerts':[]},'immunity':{'flags':[]}}
class T(unittest.TestCase):
 def reject(self,**changes):
  g=Guardian();d={**BASE,**changes}
  with self.assertRaises(GuardianRejected):checked_scan(g,**d)
  self.assertEqual(g.calls,0)
 def test_valid(self):
  g=Guardian();self.assertEqual(checked_scan(g,**BASE)['protection_score'],1.0);self.assertEqual(g.calls,1)
 def test_missing_reality(self):self.reject(reality={})
 def test_missing_immunity(self):self.reject(immunity={})
 def test_missing_coherence(self):self.reject(coherence={})
 def test_missing_explanation(self):self.reject(explanation={})
 def test_nan(self):self.reject(reality={'certainty':float('nan')})
 def test_inf(self):self.reject(reality={'certainty':float('inf')})
 def test_bool(self):self.reject(reality={'certainty':True})
 def test_out_of_range(self):self.reject(reality={'certainty':1.5})
 def test_extra(self):self.reject(reality={'certainty':.5,'authorization':'real'})
 def test_invalid_flags(self):self.reject(immunity={'flags':[5]})
 def test_invalid_tags(self):self.reject(explanation={'tags':'ok'})
 def test_invalid_coherence(self):self.reject(coherence={'alerts':None})
 def test_invalid_result(self):
  class Bad: 
   def scan(self):return {'protection_score':float('nan')}
  with self.assertRaises(GuardianRejected):checked_scan(Bad(),**BASE)
if __name__=='__main__':unittest.main()
