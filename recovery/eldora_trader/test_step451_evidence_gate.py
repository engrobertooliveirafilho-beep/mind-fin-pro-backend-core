import unittest
from step451_evidence_gate import EvidenceRejected, rank_branches

class Step451GateTests(unittest.TestCase):
    def setUp(self):
        self.branches = [{"branch_id": "b1"}, {"branch_id": "b2"}]
        self.assessments = {"b1": {"verified": True, "score": .2, "evidence_id": "e1"},
                            "b2": {"verified": True, "score": .9, "evidence_id": "e2"}}
    def test_content_evidence_overrides_position(self):
        self.assertEqual(rank_branches(self.branches, self.assessments)[0]["branch_id"], "b2")
    def test_missing_assessment(self):
        with self.assertRaises(EvidenceRejected): rank_branches(self.branches, {"b1": self.assessments["b1"]})
    def test_unverified(self):
        self.assessments["b2"]["verified"] = False
        with self.assertRaises(EvidenceRejected): rank_branches(self.branches, self.assessments)
    def test_nan(self):
        self.assessments["b1"]["score"] = float("nan")
        with self.assertRaises(EvidenceRejected): rank_branches(self.branches, self.assessments)
    def test_duplicate(self):
        with self.assertRaises(EvidenceRejected): rank_branches([self.branches[0]]*2, self.assessments)
    def test_no_evidence(self):
        self.assessments["b1"]["evidence_id"] = ""
        with self.assertRaises(EvidenceRejected): rank_branches(self.branches, self.assessments)
    def test_no_branches(self):
        with self.assertRaises(EvidenceRejected): rank_branches([], {})
    def test_boolean_score(self):
        self.assessments["b1"]["score"] = True
        with self.assertRaises(EvidenceRejected): rank_branches(self.branches, self.assessments)

if __name__ == "__main__":
    unittest.main()
