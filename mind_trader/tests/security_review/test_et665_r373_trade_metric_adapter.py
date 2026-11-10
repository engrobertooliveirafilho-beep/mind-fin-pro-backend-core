import unittest
from decimal import Decimal
from mind_trader.experimental.et665_r373_trade_metric_adapter import metrics,evaluate_trades
def windows():
    return [{"window_id":str(i),"trades":["2"]*20+["-1"]*10} for i in range(5)]
class R373(unittest.TestCase):
    def test_derived_metrics(self):
        r=metrics(["2","-1","2","-1"])
        self.assertEqual(Decimal(r["pf"]),Decimal(2))
        self.assertEqual(Decimal(r["winrate"]),Decimal(50))
        self.assertEqual(Decimal(r["expectancy"]),Decimal("0.5"))
    def test_paper_five_windows(self):
        r=evaluate_trades(windows(),True)
        self.assertEqual(r["research_gate"],"PASS")
        self.assertFalse(r["historical_fills_verified"])
        self.assertFalse(r["strategy_promotion_authorized"])
    def test_drawdown(self):
        self.assertEqual(Decimal(metrics(["2","-1","-2","3"])["max_dd_r"]),Decimal(3))
    def test_three_windows_fail(self):
        w=windows()
        for i in (0,1):w[i]["trades"]=["-1"]*30
        self.assertEqual(evaluate_trades(w,True)["research_gate"],"BLOCKED")
    def test_nan_rejected(self):
        with self.assertRaises(ValueError):metrics(["NaN"])
    def test_missing_trades_rejected(self):
        with self.assertRaises(ValueError):metrics([])
    def test_correlation_gate(self):
        self.assertEqual(evaluate_trades(windows(),False)["research_gate"],"BLOCKED")
if __name__=="__main__":unittest.main()
