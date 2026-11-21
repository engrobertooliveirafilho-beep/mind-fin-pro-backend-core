import unittest
from step453_finance import npv, solve_linear, NumericSafetyError
class TestStep453(unittest.TestCase):
    def test_npv(self): self.assertAlmostEqual(npv(.1,[-100,110]),0)
    def test_zero_rate(self): self.assertEqual(npv(0,[1,2,3]),6)
    def test_empty(self):
        with self.assertRaises(NumericSafetyError): npv(0,[])
    def test_negative_one(self):
        with self.assertRaises(NumericSafetyError): npv(-1,[1])
    def test_nan_rate(self):
        with self.assertRaises(NumericSafetyError): npv(float('nan'),[1])
    def test_inf_flow(self):
        with self.assertRaises(NumericSafetyError): npv(0,[float('inf')])
    def test_bool_flow(self):
        with self.assertRaises(NumericSafetyError): npv(0,[True])
    def test_linear(self): self.assertEqual(solve_linear(2,-4)['x'],2)
    def test_infinite(self): self.assertEqual(solve_linear(0,0)['type'],'infinite_solutions')
    def test_none(self): self.assertEqual(solve_linear(0,1)['type'],'no_solution')
    def test_nonfinite_root(self):
        with self.assertRaises(NumericSafetyError): solve_linear(1e-320,1e308)
    def test_bool_coefficient(self):
        with self.assertRaises(NumericSafetyError): solve_linear(True,1)
if __name__=='__main__': unittest.main()
