"""ET665.R367 regression: chronological boundaries, costs and no lookahead."""
import unittest
from decimal import Decimal
from mind_trader.experimental.et665_r367_chronological_backtest import run_fixed_strategy,split_chronological,backtest_segment
def bars():
    return [{"ts":i,"open":"100","close":"101","signal":1} for i in range(10)]
class R367(unittest.TestCase):
    def test_partition_no_overlap(self):
        p=split_chronological(bars())
        self.assertLess(p["train"][-1]["ts"],p["validation"][0]["ts"])
        self.assertLess(p["validation"][-1]["ts"],p["test"][0]["ts"])
    def test_costs_reduce_net(self):
        p=bars()
        a=run_fixed_strategy(p,spread_bps="0",slippage_bps="0",commission_bps="0")
        b=run_fixed_strategy(p,spread_bps="5",slippage_bps="3",commission_bps="2")
        self.assertLess(Decimal(b["results"]["train"]["net_return"]),Decimal(a["results"]["train"]["net_return"]))
        self.assertEqual(b["real_orders"],"FORBIDDEN")
        self.assertFalse(b["historical_p2405_integrated"])
    def test_current_signal_never_trades_current_bar(self):
        p=bars()
        p[0]["signal"]=0
        p[1]["signal"]=1
        r=backtest_segment(p[:2])
        self.assertEqual(r["trades"],0)
    def test_boundary_no_leak(self):
        p=bars();p[5]["signal"]=1;p[6]["signal"]=0
        r=run_fixed_strategy(p)
        self.assertEqual(r["results"]["validation"]["trades"],0)
    def test_duplicate_or_unsorted_rejected(self):
        p=bars();p[4]["ts"]=3
        with self.assertRaises(ValueError):split_chronological(p)
        p=bars();p[4]["ts"]=100
        with self.assertRaises(ValueError):split_chronological(p)
    def test_invalid_price_and_cost_rejected(self):
        p=bars();p[0]["open"]="NaN"
        with self.assertRaises(ValueError):split_chronological(p)
        with self.assertRaises(ValueError):run_fixed_strategy(bars(),spread_bps="-1")
if __name__=="__main__":unittest.main()
