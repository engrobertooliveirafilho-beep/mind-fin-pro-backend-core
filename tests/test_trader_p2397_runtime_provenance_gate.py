import unittest
from src.revisions.trader_p2397_runtime_provenance_gate import assess_runtime


class RuntimeProvenanceGateTests(unittest.TestCase):
    def setUp(self):
        self.score = {"decision": "OBSERVE_SCORE", "final_score": 68.391266}
        self.router = {"allowed": False, "route": "OBSERVE_ONLY"}
        self.ensemble = {"allowed": False, "vote": "OBSERVE_ONLY",
                         "operational_members": 0, "quorum": 2}
        self.policy = {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
                       "ftmo_real": "FORBIDDEN", "runtime_modification_allowed": False,
                       "broker_execution_allowed": False, "ftmo_real_allowed": False}

    def test_historical_observe_blocks(self):
        self.assertFalse(assess_runtime(self.score, self.router, self.ensemble, self.policy)["allowed"])

    def test_missing_policy_blocks(self):
        self.assertFalse(assess_runtime(self.score, self.router, self.ensemble, {})["allowed"])

    def test_forged_upstream_promotion_cannot_override_policy(self):
        self.score = {"decision": "PROMOTE_SCORE", "final_score": 99}
        self.router = {"allowed": True, "route": "PAPER_OPERATIONAL"}
        self.ensemble = {"allowed": True, "vote": "PAPER_OPERATIONAL",
                         "operational_members": 3, "quorum": 2}
        self.assertFalse(assess_runtime(self.score, self.router, self.ensemble, self.policy)["allowed"])

    def test_invalid_numeric_score_blocks(self):
        for score in (float("nan"), "99", True):
            with self.subTest(score=score):
                self.score = {"decision": "PROMOTE_SCORE", "final_score": score}
                self.assertFalse(assess_runtime(self.score, self.router, self.ensemble, self.policy)["allowed"])


if __name__ == "__main__":
    unittest.main()
