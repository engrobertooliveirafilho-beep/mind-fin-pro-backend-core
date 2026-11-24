import unittest
from app.runtime.p2395_context_router_v2 import build_router
from app.runtime.p2396_edge_ensemble import build_ensemble

class P2395Tests(unittest.TestCase):
    def setUp(self):
        self.edge = {
            "decision": "PROMOTE_SCORE", "final_score": 72.5,
            "key": "US_AM|SWEEP|REVERSAL", "direction": "BUY",
            "cluster_id": "CLUSTER_A", "source_candidate_id": "EDGE_A",
        }

    def test_matching_context_is_candidate(self):
        result = build_router(self.edge).route({"key": self.edge["key"], "direction": "BUY"})
        self.assertTrue(result.allowed)
        self.assertEqual(result.route, "PAPER_SIGNAL_CANDIDATE")
        self.assertFalse(result.real_execution_allowed)
        self.assertEqual(result.decision, "PAPER_ELIGIBLE")

    def test_context_key_mismatch_observe(self):
        result = build_router(self.edge).route({"key": "OTHER", "direction": "BUY"})
        self.assertEqual(result.reason, "CONTEXT_KEY_MISMATCH")

    def test_context_direction_mismatch_observe(self):
        result = build_router(self.edge).route({"key": self.edge["key"], "direction": "SELL"})
        self.assertEqual(result.reason, "CONTEXT_DIRECTION_MISMATCH")

    def test_missing_context_observe(self):
        self.assertEqual(build_router(self.edge).route({}).route, "OBSERVE_ONLY")

    def test_non_mapping_context_observe(self):
        self.assertEqual(build_router(self.edge).route(None).reason, "INVALID_CONTEXT")

    def test_non_promoted_stays_observe(self):
        edge = {**self.edge, "decision": "OBSERVE_SCORE"}
        self.assertEqual(build_router(edge).route({}).reason, "EDGE_NOT_PROMOTED_SCORE_72.5")

    def test_nan_score_observe(self):
        edge = {**self.edge, "final_score": float("nan")}
        self.assertEqual(build_router(edge).route({"key": edge["key"], "direction": "BUY"}).reason, "INVALID_EDGE_SCORE")

    def test_missing_lineage_observe(self):
        edge = {**self.edge, "source_candidate_id": ""}
        self.assertEqual(build_router(edge).route({"key": edge["key"], "direction": "BUY"}).reason, "MISSING_SOURCE_EDGE")


class P2396Tests(unittest.TestCase):
    def setUp(self):
        self.a = self.member("EDGE_A")
        self.b = self.member("EDGE_B")

    @staticmethod
    def member(edge):
        return {
            "allowed": True, "route": "PAPER_SIGNAL_CANDIDATE", "decision": "PAPER_ELIGIBLE",
            "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
            "ftmo_real": "FORBIDDEN", "real_execution_allowed": False,
            "edge_status": "PROMOTE_SCORE", "edge_score_decision": "PROMOTE_SCORE",
            "source_cluster": "CLUSTER_A", "source_edge": edge, "edge_score": 72.5,
        }

    def test_p2395_outputs_feed_p2396_contract(self):
        edges = [
            {"decision": "PROMOTE_SCORE", "final_score": 72.5, "key": "K1",
             "direction": "BUY", "cluster_id": "CL1", "source_candidate_id": "E1"},
            {"decision": "PROMOTE_SCORE", "final_score": 74.0, "key": "K2",
             "direction": "SELL", "cluster_id": "CL2", "source_candidate_id": "E2"},
        ]
        records = [
            build_router(edge).route({"key": edge["key"], "direction": edge["direction"]}).as_dict()
            for edge in edges
        ]
        vote = build_ensemble(records).vote()
        self.assertTrue(vote.allowed)
        self.assertEqual(vote.decision, "PAPER_ELIGIBLE")
        self.assertFalse(vote.real_execution_allowed)

    def test_one_historical_candidate_cannot_reach_quorum(self):
        vote = build_ensemble([{"allowed": False, "route": "OBSERVE_ONLY"}]).vote()
        self.assertFalse(vote.allowed)
        self.assertEqual(vote.operational_members, 0)

    def test_two_distinct_lineaged_members_reach_paper_candidate(self):
        vote = build_ensemble([self.a, self.b]).vote()
        self.assertTrue(vote.allowed)
        self.assertEqual(vote.operational_members, 2)
        self.assertEqual(vote.vote, "PAPER_ELIGIBLE")
        self.assertEqual(vote.decision, "PAPER_ELIGIBLE")
        self.assertFalse(vote.real_execution_allowed)

    def test_duplicate_source_edge_not_double_counted(self):
        vote = build_ensemble([self.a, self.a]).vote()
        self.assertFalse(vote.allowed)
        self.assertEqual(vote.operational_members, 0)
        self.assertEqual(vote.reason, "DUPLICATE_SOURCE_EDGE")

    def test_missing_lineage_not_counted(self):
        bad = {**self.a, "source_edge": ""}
        self.assertEqual(build_ensemble([bad, self.b]).vote().operational_members, 1)

    def test_real_execution_authority_rejected(self):
        bad = {**self.a, "real_execution_allowed": True}
        self.assertEqual(build_ensemble([bad, self.b]).vote().operational_members, 1)

    def test_wrong_mode_rejected(self):
        bad = {**self.a, "mode": "LIVE"}
        self.assertEqual(build_ensemble([bad, self.b]).vote().operational_members, 1)

    def test_wrong_decision_rejected(self):
        bad = {**self.a, "edge_score_decision": "OBSERVE_SCORE"}
        self.assertEqual(build_ensemble([bad, self.b]).vote().operational_members, 1)

    def test_bool_quorum_rejected(self):
        self.assertEqual(build_ensemble([self.a, self.b], quorum=True).vote().reason, "INVALID_QUORUM")

    def test_zero_quorum_rejected(self):
        self.assertEqual(build_ensemble([self.a, self.b], quorum=0).vote().reason, "INVALID_QUORUM")

    def test_nonfinite_score_rejected(self):
        bad = {**self.a, "edge_score": float("inf")}
        self.assertEqual(build_ensemble([bad, self.b]).vote().operational_members, 1)

if __name__ == "__main__":
    unittest.main()
