import copy,unittest
from mind_trader.experimental.et665_r375_measured_walk_forward import evaluate_portfolio

def sample():
    a=["2"]*20+["-1"]*10
    b=["2"]*10+["-1"]*10+["2"]*10
    return {"a":[{"window_id":str(i),"trades":a[:]} for i in range(5)],
            "b":[{"window_id":str(i),"trades":b[:]} for i in range(5)]}
class R375(unittest.TestCase):
    def test_measured_correlation(self):
        r=evaluate_portfolio(sample())
        self.assertEqual(r["status"],"RESEARCH_GATE_PASS")
        self.assertEqual(r["correlation_source"],"MEASURED_NOT_SELF_ATTESTED")
        self.assertFalse(r["official_p2405f_certified"])
        self.assertFalse(r["strategy_promotion_authorized"])
    def test_identical_strategy_blocked(self):
        s=sample();s["b"]=copy.deepcopy(s["a"])
        self.assertEqual(evaluate_portfolio(s)["status"],"BLOCKED")
    def test_strategy_policy_failure(self):
        s=sample();s["b"][0]["trades"]=["-1"]*30;s["b"][1]["trades"]=["-1"]*30
        self.assertEqual(evaluate_portfolio(s)["status"],"BLOCKED")
    def test_misaligned_window_rejected(self):
        s=sample();s["b"][0]["window_id"]="wrong"
        with self.assertRaises(ValueError):evaluate_portfolio(s)
    def test_invalid_threshold_rejected(self):
        with self.assertRaises(ValueError):evaluate_portfolio(sample(),"1")
if __name__=="__main__":unittest.main()
