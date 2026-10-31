import unittest
from recovery.r342_de40.causal_gates import causal_signal,score_next_candle,certification_report

class CausalGatesTest(unittest.TestCase):
    def test_signal_cannot_depend_on_future(self):
        prev={"close":100}; current={"close":101,"high":102,"low":100}
        direction=causal_signal(current,prev)
        self.assertEqual(direction,1)
        self.assertLess(score_next_candle(current,{"close":99},direction),0)
        self.assertGreater(score_next_candle(current,{"close":103},direction),0)
        self.assertEqual(causal_signal(current,prev),direction)
    def test_flat_is_no_trade(self):
        self.assertEqual(causal_signal({"close":100},{"close":100}),0)
        self.assertIsNone(score_next_candle({"close":100,"high":101,"low":99},{"close":102},0))
    def test_invalid_candle_fails_closed(self):
        with self.assertRaises(ValueError):
            score_next_candle({"close":100,"high":100,"low":100},{"close":101},1)
    def test_success_alone_never_certifies(self):
        report=certification_report(success=True,source_sha_verified=False,oos_independent=False,ci_pass=False,no_lookahead=True,chronology_pass=False)
        self.assertEqual(report["status"],"BLOCKED")
        self.assertFalse(report["promotion_authorized"])
    def test_all_gates_still_do_not_promote(self):
        report=certification_report(success=True,source_sha_verified=True,oos_independent=True,ci_pass=True,no_lookahead=True,chronology_pass=True)
        self.assertEqual(report["status"],"CERTIFIED")
        self.assertFalse(report["promotion_authorized"])
if __name__=="__main__":unittest.main()
