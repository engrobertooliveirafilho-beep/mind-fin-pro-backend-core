import unittest

from app.runtime.p2091_2100_realtime_intelligence_layer import (
    extract_specialists,
    PerformanceAttribution,
    SpecialistRankingEvolution,
    load_json,
)

class RealDNAEvidenceIntegrityTests(unittest.TestCase):
    def test_missing_portfolio_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "REALDNA_SPECIALISTS_MISSING_OR_EMPTY"):
            extract_specialists({})

    def test_empty_portfolio_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "REALDNA_SPECIALISTS_MISSING_OR_EMPTY"):
            extract_specialists({"specialists": []})

    def test_missing_or_duplicate_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "REALDNA_SPECIALIST_ID_MISSING"):
            extract_specialists([{"type": "RANGE_REVERSION"}])
        with self.assertRaisesRegex(ValueError, "REALDNA_SPECIALIST_ID_DUPLICATE"):
            extract_specialists([{"id": "A"}, {"id": "A"}])

    def test_ranking_requires_observed_scores(self):
        result = SpecialistRankingEvolution().evaluate([{"id": "A"}, {"id": "B"}, {"id": "C"}])
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.reason, "SPECIALIST_EVIDENCE_SCORE_MISSING")

    def test_attribution_does_not_split_portfolio_pnl_equally(self):
        result = PerformanceAttribution().evaluate(
            [{"id": "A"}, {"id": "B"}, {"id": "C"}],
            {"metrics": {"paper_realized_pnl": -90, "paper_mark_to_market_pnl": -100}},
        )
        self.assertEqual(result.status, "FAIL")
        self.assertIsNone(result.payload["attribution_sum"])
        self.assertEqual(result.payload["attribution"], {})

if __name__ == "__main__":
    unittest.main()
