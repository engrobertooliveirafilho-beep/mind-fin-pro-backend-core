import unittest
from mind_trader.research.et665_r40_guarded_research import (
    ResearchRejected, validate_walk_forward, anti_overfit_validate,
    portfolio_exposure, correlation_precheck, safety_contract,
)
class R40Tests(unittest.TestCase):
    def sample(self):
        return {"train_start":"2024-01-01","train_end":"2024-06-01","test_start":"2024-07-01","test_end":"2024-12-01","train_profit_factor":2,"test_profit_factor":1.8,"test_payoff":3.1,"test_trades":31,"test_max_drawdown":8}
    def edge(self):
        return dict(symbols_tested=3,years_tested=3,regimes_tested=3,out_of_sample_profit_factor=1.6,out_of_sample_payoff=3.2,out_of_sample_expectancy=.1,max_drawdown=8,parameter_sensitivity=20)
    def test_valid_walk_forward_research_only(self):
        self.assertTrue(validate_walk_forward([self.sample()])["all_passed"])
        self.assertFalse(validate_walk_forward([self.sample()])["promotion_allowed"])
    def test_missing_period_rejected(self):
        s=self.sample(); del s["train_start"]
        with self.assertRaises(ResearchRejected):validate_walk_forward([s])
    def test_overlap_rejected(self):
        s=self.sample();s["test_start"]="2024-05-01"
        with self.assertRaises(ResearchRejected):validate_walk_forward([s])
    def test_empty_rejected(self):
        with self.assertRaises(ResearchRejected):validate_walk_forward([])
    def test_nan_rejected(self):
        s=self.sample();s["test_profit_factor"]=float("nan")
        with self.assertRaises(ResearchRejected):validate_walk_forward([s])
    def test_anti_overfit_research_only(self):
        self.assertTrue(anti_overfit_validate(self.edge())["passed"])
        self.assertFalse(anti_overfit_validate(self.edge())["promotion_allowed"])
    def test_anti_overfit_missing_rejected(self):
        e=self.edge();del e["years_tested"]
        with self.assertRaises(ResearchRejected):anti_overfit_validate(e)
    def test_anti_overfit_infinite_rejected(self):
        e=self.edge();e["max_drawdown"]=float("inf")
        with self.assertRaises(ResearchRejected):anti_overfit_validate(e)
    def test_unknown_symbol_rejected(self):
        with self.assertRaises(ResearchRejected):portfolio_exposure([{"symbol":"UNKNOWN","side":"BUY","lot":.01}])
    def test_unknown_side_rejected(self):
        with self.assertRaises(ResearchRejected):portfolio_exposure([{"symbol":"EURUSD","side":"HOLD","lot":.01}])
    def test_invalid_lot_rejected(self):
        with self.assertRaises(ResearchRejected):portfolio_exposure([{"symbol":"EURUSD","side":"BUY","lot":0}])
    def test_currency_direction(self):
        e=portfolio_exposure([{"symbol":"EURUSD","side":"BUY","lot":.01}])["exposure_lot_proxy"]
        self.assertEqual(e["EUR"],.01);self.assertEqual(e["USD"],-.01)
    def test_concentration_blocks(self):
        self.assertFalse(correlation_precheck([{"symbol":"EURUSD","side":"BUY","lot":.02}],{"symbol":"GBPUSD","side":"BUY","lot":.02})["approved"])
    def test_safety(self):
        self.assertFalse(safety_contract()["operational_certified"])
        self.assertEqual(safety_contract()["real_orders"],"FORBIDDEN")
if __name__=="__main__":unittest.main()
