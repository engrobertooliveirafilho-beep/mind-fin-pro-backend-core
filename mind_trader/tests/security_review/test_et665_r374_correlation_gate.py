import unittest
from mind_trader.experimental.et665_r374_correlation_gate import assess,correlation
class R374(unittest.TestCase):
    def test_identical_blocked(self):
        self.assertEqual(assess({"a":[1,2,3,4],"b":[1,2,3,4]})["status"],"BLOCKED")
    def test_inverse_blocked(self):
        self.assertEqual(assess({"a":[1,2,3,4],"b":[4,3,2,1]})["status"],"BLOCKED")
    def test_orthogonal_pass(self):
        self.assertEqual(assess({"a":[1,2,3,4],"b":[1,-1,-1,1]})["status"],"PASS")
    def test_zero_variance_rejected(self):
        with self.assertRaises(ValueError):assess({"a":[1,1,1],"b":[1,2,3]})
    def test_short_rejected(self):
        with self.assertRaises(ValueError):assess({"a":[1,2],"b":[2,1]})
    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):assess({"a":[1,2,"NaN"],"b":[1,2,3]})
    def test_bad_threshold_rejected(self):
        with self.assertRaises(ValueError):assess({"a":[1,2,3],"b":[3,1,2]},"1")
    def test_paper_only(self):
        r=assess({"a":[1,2,3,4],"b":[1,-1,-1,1]})
        self.assertFalse(r["strategy_promotion_authorized"])
        self.assertEqual(r["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
