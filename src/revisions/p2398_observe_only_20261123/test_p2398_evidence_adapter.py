import json
import pathlib
import unittest
from p2398_evidence_adapter import evaluate_evidence
from p2398_observe_gate import GateRejected
HERE = pathlib.Path(__file__).resolve().parent
class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.router = json.loads((HERE / "router_contract.json").read_text())
        self.ensemble = json.loads((HERE / "ensemble_result.json").read_text())
    def test_original_evidence_observe_only(self):
        self.assertEqual(evaluate_evidence(self.router, self.ensemble)["decision"], "OBSERVE_ONLY")
    def test_unexpected_evidence_fields_rejected(self):
        with self.assertRaises(GateRejected):
            evaluate_evidence({**self.router, "order_dispatch": True}, self.ensemble)
        with self.assertRaises(GateRejected):
            evaluate_evidence(self.router, {**self.ensemble, "runtime_promotion": True})
    def test_router_mutations_rejected(self):
        for key, value in [("input_edge_decision", "PROMOTE_SCORE"),
                           ("route_result", "OPERATE"), ("real_execution_allowed", True),
                           ("mode", "LIVE"), ("real_orders", "ALLOWED")]:
            with self.subTest(key=key), self.assertRaises(GateRejected):
                evaluate_evidence({**self.router, key: value}, self.ensemble)
    def test_ensemble_mutations_rejected(self):
        for key, value in [("allowed", True), ("vote", "OPERATE"),
                           ("operational_members", 1), ("quorum", 1),
                           ("members", 2), ("ftmo_real", "ALLOWED")]:
            with self.subTest(key=key), self.assertRaises(GateRejected):
                evaluate_evidence(self.router, {**self.ensemble, key: value})
if __name__ == "__main__":
    unittest.main()
