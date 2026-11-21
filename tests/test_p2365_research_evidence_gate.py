import unittest
from app.runtime.p2365_research_evidence_gate import assess_p2365_context


class P2365ResearchGateTests(unittest.TestCase):
    def setUp(self):
        self.summary = dict(source_rows=100000, contexts_ranked=89, promoted_contexts=0,
                            mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN",
                            symbol="DE40", source_timeframe="M5")

    def test_historical_summary_is_not_certified_without_oos(self):
        self.assertFalse(assess_p2365_context(self.summary)["approved"])

    def test_verified_research_never_promotes(self):
        result = assess_p2365_context(self.summary, chronological_oos_verified=True,
                                      independent_lineage_verified=True)
        self.assertFalse(result["approved"])
        self.assertEqual(result["decision"], "RESEARCH_EVIDENCE_ACCEPTED_NO_PROMOTION")

    def test_invalid_or_promoted_summary_blocks(self):
        for patch in ({"promoted_contexts": 1}, {"source_rows": -1},
                      {"contexts_ranked": "89"}, {"real_orders": "ALLOWED"},
                      {"symbol": "EURUSD"}):
            with self.subTest(patch=patch):
                result = assess_p2365_context(dict(self.summary, **patch),
                    chronological_oos_verified=True, independent_lineage_verified=True)
                self.assertFalse(result["approved"])
                self.assertNotEqual(result["decision"], "RESEARCH_EVIDENCE_ACCEPTED_NO_PROMOTION")

    def test_truthy_flags_do_not_pass(self):
        self.assertEqual(assess_p2365_context(self.summary, chronological_oos_verified="true",
            independent_lineage_verified=True)["decision"], "BLOCK_OOS_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
