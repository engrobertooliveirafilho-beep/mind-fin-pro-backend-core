import unittest
from mind_trader.experimental.et665_r372_walk_forward_policy import evaluate
def rows():
    return [{"window_id":str(i),"samples":40,"pf":"1.6","winrate":"48",
             "expectancy":"0.1","max_dd_r":"11"} for i in range(5)]
class R372(unittest.TestCase):
    def test_five_windows_pass_research_only(self):
        r=evaluate(rows(),True)
        self.assertEqual(r["research_gate"],"PASS")
        self.assertFalse(r["strategy_promotion_authorized"])
        self.assertFalse(r["historical_fills_verified"])
    def test_four_of_five_pass(self):
        r=rows();r[0]["pf"]="1.4"
        self.assertEqual(evaluate(r,True)["research_gate"],"PASS")
    def test_three_of_five_block(self):
        r=rows();r[0]["pf"]="1.4";r[1]["pf"]="1.4"
        self.assertEqual(evaluate(r,True)["research_gate"],"BLOCKED")
    def test_correlation_required(self):
        self.assertEqual(evaluate(rows(),False)["research_gate"],"BLOCKED")
    def test_min_samples_and_expectancy(self):
        r=rows();r[0]["samples"]=29;r[1]["expectancy"]="0"
        self.assertEqual(evaluate(r,True)["research_gate"],"BLOCKED")
    def test_duplicate_windows_rejected(self):
        r=rows();r[1]["window_id"]="0"
        with self.assertRaises(ValueError):evaluate(r,True)
    def test_nonfinite_rejected(self):
        r=rows();r[0]["pf"]="NaN"
        with self.assertRaises(ValueError):evaluate(r,True)
    def test_missing_window_rejected(self):
        with self.assertRaises(ValueError):evaluate(rows()[:4],True)
if __name__=="__main__":unittest.main()
