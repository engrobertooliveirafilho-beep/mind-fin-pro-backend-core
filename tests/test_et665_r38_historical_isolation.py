import unittest
from mind_trader.app.research.et665_r38_historical_validation_gates import walk_forward,anti_overfit,currency_exposure

class R38HistoricalIsolationTests(unittest.TestCase):
    def windows(self):
        return [dict(train_start=f"2020-01-0{i}",train_end=f"2020-02-0{i}",test_start=f"2020-03-0{i}",test_end=f"2020-04-0{i}",train_pf=1.7,test_pf=1.6,test_payoff=3.2,test_drawdown=4,test_trades=35) for i in (1,2,3)]
    def test_walk_forward_research_only(self):
        self.assertEqual(walk_forward(self.windows())["decision"],"RESEARCH_REVIEW_ONLY")
    def test_walk_forward_leakage_block(self):
        w=self.windows();w[0]["test_start"]=w[0]["train_end"]
        self.assertEqual(walk_forward(w)["reason"],"LEAKAGE_OR_OVERLAP")
    def test_walk_forward_nan_block(self):
        w=self.windows();w[0]["test_pf"]=float("nan")
        self.assertEqual(walk_forward(w)["reason"],"INVALID_METRICS")
    def test_walk_forward_overlap_block(self):
        w=self.windows();w[1]["test_start"]=w[0]["test_end"]
        self.assertEqual(walk_forward(w)["reason"],"OVERLAPPING_TEST_WINDOWS")
    def test_anti_overfit_requires_provenance(self):
        self.assertEqual(anti_overfit({})["reason"],"UNVERIFIED_PROVENANCE")
    def test_anti_overfit_valid_is_never_promoted(self):
        m=dict(source_verified=True,out_of_sample_verified=True,symbols_tested=3,years_tested=3,regimes_tested=3,out_of_sample_profit_factor=1.6,out_of_sample_payoff=3.2,out_of_sample_expectancy=.1,max_drawdown=5,parameter_sensitivity=12)
        self.assertEqual(anti_overfit(m)["decision"],"RESEARCH_REVIEW_ONLY")
    def test_unknown_asset_blocked(self):
        self.assertEqual(currency_exposure([],dict(symbol="XAUUSD",side="BUY",lot=.01))["reason"],"UNKNOWN_ASSET_OR_UNITS")
    def test_correlated_currency_blocked(self):
        self.assertEqual(currency_exposure([dict(symbol="EURUSD",side="BUY",lot=.02)],dict(symbol="GBPUSD",side="BUY",lot=.02))["reason"],"CURRENCY_CONCENTRATION")
    def test_valid_exposure_research_only(self):
        self.assertEqual(currency_exposure([],dict(symbol="EURUSD",side="BUY",lot=.01))["decision"],"RESEARCH_REVIEW_ONLY")

if __name__=="__main__":
    unittest.main()
