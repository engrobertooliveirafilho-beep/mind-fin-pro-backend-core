import unittest
from app.runtime.p2373_parametric_batch_coverage_gate import evaluate_batch_coverage


class P2373BatchCoverageTests(unittest.TestCase):
    def test_historical_partial_batch_is_not_certified(self):
        r = evaluate_batch_coverage(78000, 5000, 52, 4948, 0)
        self.assertEqual(r["untested"], 73000)
        self.assertFalse(r["coverage_complete"])
        self.assertFalse(r["promotion_allowed"])
        self.assertTrue(r["walk_forward_required"])
        self.assertEqual(r["ftmo_real"], "FORBIDDEN")

    def test_inconsistent_counts_rejected(self):
        with self.assertRaisesRegex(ValueError, "INCONSISTENT_BATCH_COUNTS"):
            evaluate_batch_coverage(78000, 5000, 52, 4947, 0)

    def test_boolean_counts_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_BATCH_COUNTS"):
            evaluate_batch_coverage(78000, True, 0, 1, 0)


if __name__ == "__main__":
    unittest.main()
