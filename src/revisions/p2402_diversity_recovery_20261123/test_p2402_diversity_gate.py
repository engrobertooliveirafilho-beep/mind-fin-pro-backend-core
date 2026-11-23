import unittest
from p2402_diversity_gate import validate_p2402,certification
class Tests(unittest.TestCase):
    def setUp(self):
        self.s={"mission":"P2402_CONTEXT_DIVERSITY_CLUSTERING","mode":"PAPER_ONLY",
        "real_orders":"FORBIDDEN","ftmo_real":"FORBIDDEN","promoted_input":34,
        "structural_clusters":29,"representatives":29,"selected_pool":20,
        "families":18,"max_per_family":2,"runtime_promotion_allowed":False,
        "real_execution_allowed":False,"next_required":"P2403_CORRELATION_ANALYZER",
        "correlation":"NOT_MEASURED_YET"}
    def test_valid(self): self.assertTrue(validate_p2402(self.s))
    def test_no_promotion(self): self.assertFalse(validate_p2402({**self.s,"runtime_promotion_allowed":True}))
    def test_no_correlation_claim(self): self.assertFalse(validate_p2402({**self.s,"correlation":"MEASURED"}))
    def test_not_performance_certified(self): self.assertFalse(certification(self.s)["performance_certified"])
if __name__=="__main__": unittest.main()
