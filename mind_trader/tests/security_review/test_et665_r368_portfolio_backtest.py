"""ET665.R368: portfolio regression and adversarial alignment checks."""
import unittest
from decimal import Decimal
from mind_trader.experimental.et665_r368_portfolio_backtest import portfolio

def bars(signal):
    return [{"ts":i,"open":"100","close":"101","signal":signal} for i in range(10)]
class R368(unittest.TestCase):
    def test_two_independent_strategies(self):
        r=portfolio({"long":bars(1),"short":bars(-1)},{"long":"0.75","short":"0.25"},spread_bps="2",slippage_bps="1",commission_bps="1")
        self.assertEqual(set(r["strategies"]),{"long","short"})
        self.assertEqual(r["real_orders"],"FORBIDDEN")
        self.assertFalse(r["historical_p2405_integrated"])
        self.assertLess(Decimal(r["portfolio"]["train"]["weighted_net_return"]),Decimal(r["strategies"]["long"]["results"]["train"]["net_return"]))
    def test_misaligned_histories_rejected(self):
        x=bars(1);y=bars(-1);y[5]["close"]="102"
        with self.assertRaisesRegex(ValueError,"misaligned"):
            portfolio({"a":x,"b":y},{"a":"0.5","b":"0.5"})
    def test_bad_weights_rejected(self):
        with self.assertRaises(ValueError):
            portfolio({"a":bars(1),"b":bars(-1)},{"a":"0.7","b":"0.7"})
    def test_nonfinite_weights_rejected(self):
        with self.assertRaises(ValueError):
            portfolio({"a":bars(1),"b":bars(-1)},{"a":"NaN","b":"0.5"})
    def test_no_same_bar_execution(self):
        x=bars(0);y=bars(0);x[0]["signal"]=1;y[0]["signal"]=-1
        r=portfolio({"a":x,"b":y},{"a":"0.5","b":"0.5"})
        self.assertEqual(r["portfolio"]["validation"]["total_trades"],0)
        self.assertEqual(r["portfolio"]["test"]["total_trades"],0)
if __name__=="__main__":unittest.main()
