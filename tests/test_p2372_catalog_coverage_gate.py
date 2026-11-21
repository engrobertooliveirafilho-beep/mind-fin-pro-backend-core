import unittest
from app.runtime.p2372_catalog_coverage_gate import reconcile_catalog_coverage


def row(timeframe, variant="A"):
    return {"family": "TREND", "variant": variant, "profile": "SCALP", "timeframe": timeframe}


class P2372CoverageTests(unittest.TestCase):
    def test_missing_m2_is_explicit_and_never_promoted(self):
        out = reconcile_catalog_coverage([row("M1"), row("M2")], [row("M1")])
        self.assertEqual(out["not_backtested_by_timeframe"], {"M2": 1})
        self.assertFalse(out["coverage_complete"])
        self.assertFalse(out["promotion_allowed"])
        self.assertFalse(out["synthetic_m2_allowed"])
        self.assertEqual(out["real_orders"], "FORBIDDEN")

    def test_unrecognized_tested_key_rejected(self):
        with self.assertRaisesRegex(ValueError, "TESTED_STRATEGY_NOT_IN_CATALOG"):
            reconcile_catalog_coverage([row("M1")], [row("M2")])

    def test_duplicate_catalog_rejected(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE_STRATEGY_KEY"):
            reconcile_catalog_coverage([row("M1"), row("M1")], [])

    def test_invalid_envelope_rejected(self):
        with self.assertRaises(ValueError):
            reconcile_catalog_coverage(None, [])


if __name__ == "__main__":
    unittest.main()
