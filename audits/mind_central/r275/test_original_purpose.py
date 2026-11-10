import unittest
from purpose_kernel import PurposeKernel
from secure_cognitive_gateway import execute,GateRejected
P={'user_benefit':.7,'safety':.9,'long_term':.8,'cashflow':.5,'learning':.6}
class Tests(unittest.TestCase):
 def test_original_nan_inflation(self):
  raw=PurposeKernel().evaluate_action({'scores':{**P,'safety':float('nan')}})
  self.assertEqual(raw['scores']['safety'],1.0)
 def test_gateway_blocks_nan(self):
  with self.assertRaises(GateRejected):execute('purpose',PurposeKernel(),{'scores':{**P,'safety':float('nan')}})
 def test_gateway_valid_real_engine(self):
  result=execute('purpose',PurposeKernel(),{'scores':P})
  self.assertAlmostEqual(result['alignment_score'],sum(P[k]*v for k,v in PurposeKernel()._weights.items()))
 def test_gateway_denies_auth_metadata(self):
  with self.assertRaises(GateRejected):execute('purpose',PurposeKernel(),{'scores':P,'authorization':'REAL_ORDERS'})
if __name__=='__main__':unittest.main()
