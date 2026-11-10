import unittest
from finite_scores import finite_score, validate_scores, InvalidScore

class TestFiniteScores(unittest.TestCase):
    def test_valid_bounds(self):
        for value in [0, 0.0, .25, 1, 1.0]:
            with self.subTest(value=value): self.assertEqual(finite_score(value),float(value))
    def test_nonfinite(self):
        for value in [float('nan'),float('inf'),-float('inf')]:
            with self.subTest(value=value):
                with self.assertRaises(InvalidScore): finite_score(value)
    def test_out_of_range(self):
        for value in [-.001,1.001,1e100]:
            with self.subTest(value=value):
                with self.assertRaises(InvalidScore): finite_score(value)
    def test_type_confusion(self):
        for value in [True,False,'1','nan',None,{},[]]:
            with self.subTest(value=repr(value)):
                with self.assertRaises(InvalidScore): finite_score(value)
    def test_dimensions(self):
        dims=['user_benefit','safety']
        self.assertEqual(validate_scores({'user_benefit':.8,'safety':.9},dims),{'user_benefit':.8,'safety':.9})
    def test_missing_dimensions(self):
        with self.assertRaises(InvalidScore): validate_scores({'safety':.9},['safety','user_benefit'])
    def test_extra_dimensions(self):
        with self.assertRaises(InvalidScore): validate_scores({'safety':.9,'x':1},['safety'])
    def test_nonfinite_dimension(self):
        with self.assertRaises(InvalidScore): validate_scores({'safety':float('nan')},['safety'])
    def test_non_dict(self):
        with self.assertRaises(InvalidScore): validate_scores(None,['safety'])

if __name__=='__main__': unittest.main()
