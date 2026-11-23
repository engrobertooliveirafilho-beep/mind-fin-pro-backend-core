import unittest
from p2400_summary_gate import validate_p2400

class P2400Tests(unittest.TestCase):
    def setUp(self):
        self.summary={"mission":"P2400_RESEARCH_SPACE_EXPANSION","mode":"PAPER_ONLY",
            "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
            "generated_candidates":7500,"exported_candidates":500,
            "context_families":45,"runtime_promotion_allowed":False,
            "research_allowed":True,"real_execution_allowed":False,
            "next_required":"P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"}
        self.policy={"mission":"P2400_RESEARCH_SPACE_EXPANSION","mode":"PAPER_ONLY",
            "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN",
            "runtime_allowed":False,"research_only":True,
            "validation_required_next":"P2401_MULTI_EDGE_WALK_FORWARD_DD_FILTER"}
    def test_historical_contract(self):
        self.assertTrue(validate_p2400(self.summary,self.policy))
    def test_no_runtime_promotion(self):
        self.assertFalse(validate_p2400({**self.summary,"runtime_promotion_allowed":True},self.policy))
    def test_no_real_orders(self):
        self.assertFalse(validate_p2400(self.summary,{**self.policy,"real_orders":"ALLOWED"}))
    def test_no_false_as_zero(self):
        self.assertFalse(validate_p2400({**self.summary,"runtime_promotion_allowed":0},self.policy))
    def test_next_step_integrity(self):
        self.assertFalse(validate_p2400(self.summary,{**self.policy,"validation_required_next":"P2402"}))
if __name__=="__main__":
    unittest.main()
