import copy,unittest
from mind_trader.experimental.et665_r376_timestamp_alignment import evaluate_timestamped_portfolio

def sample():
    a=["2"]*20+["-1"]*10;b=["2"]*10+["-1"]*10+["2"]*10
    def build(values):
        return [{"window_id":str(i),"trades":[{"ts":i*100+j,"r":v} for j,v in enumerate(values)]} for i in range(5)]
    return {"a":build(a),"b":build(b)}
class R376(unittest.TestCase):
    def test_aligned_research_only(self):
        r=evaluate_timestamped_portfolio(sample())
        self.assertEqual(r["alignment"],"EXACT_TIMESTAMP_MATCH")
        self.assertEqual(r["status"],"RESEARCH_GATE_PASS")
        self.assertFalse(r["historical_fills_verified"])
    def test_missing_timestamp_rejected(self):
        s=sample();del s["b"][0]["trades"][0]["ts"]
        with self.assertRaises(ValueError):evaluate_timestamped_portfolio(s)
    def test_misaligned_timestamp_rejected(self):
        s=sample();s["b"][0]["trades"][0]["ts"]=99
        with self.assertRaises(ValueError):evaluate_timestamped_portfolio(s)
    def test_duplicate_timestamp_rejected(self):
        s=sample();s["a"][0]["trades"][1]["ts"]=0
        with self.assertRaises(ValueError):evaluate_timestamped_portfolio(s)
    def test_reversed_timestamp_rejected(self):
        s=sample();s["a"][0]["trades"][1]["ts"]=-1
        with self.assertRaises(ValueError):evaluate_timestamped_portfolio(s)
    def test_nonfinite_return_rejected(self):
        s=sample();s["a"][0]["trades"][1]["r"]="NaN"
        with self.assertRaises(ValueError):evaluate_timestamped_portfolio(s)
if __name__=="__main__":unittest.main()
