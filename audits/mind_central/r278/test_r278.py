import unittest, math
from immunity import CognitiveImmuneSystem
class R278(unittest.TestCase):
 def test_nan_unflagged(self):
  x=CognitiveImmuneSystem().scan({'score':float('nan')}); self.assertEqual(x['flags'],[]); self.assertTrue(math.isnan(x['normalized_score']))
 def test_bool_unflagged(self):self.assertEqual(CognitiveImmuneSystem().scan({'score':True})['flags'],[])
 def test_missing_score_defaults_zero(self):self.assertEqual(CognitiveImmuneSystem().scan({})['normalized_score'],0)
 def test_string_flagged(self):self.assertEqual(CognitiveImmuneSystem().scan({'score':'x'})['flags'],['invalid_score_type'])
 def test_out_of_bounds_flagged(self):self.assertEqual(CognitiveImmuneSystem().scan({'score':2})['flags'],['out_of_bounds'])
 def test_infinite_clamped(self):self.assertEqual(CognitiveImmuneSystem().scan({'score':float('inf')})['normalized_score'],1)
if __name__=='__main__':unittest.main()
