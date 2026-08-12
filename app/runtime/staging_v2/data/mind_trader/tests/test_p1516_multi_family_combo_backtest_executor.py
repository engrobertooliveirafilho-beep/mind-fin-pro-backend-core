from app.p1516_multi_family_combo_backtest_executor.engine import backtest, build_combos, monte_carlo

def test_p1516_backtest_single():
    rows=[{"close":float(i),"high":float(i),"low":float(i),"open":float(i),"volume":1000.0} for i in range(1,220)]
    r=backtest(rows,["sma_cross"])
    assert "profit_factor" in r

def test_p1516_combo_builder():
    q=[{"asset":"WINFUT","timeframe":"M15","dataset":"WINFUT_M15_normalized.csv","pattern":"sma_cross"},{"asset":"WINFUT","timeframe":"M15","dataset":"WINFUT_M15_normalized.csv","pattern":"rsi_reversion"}]
    assert any(j[4]=="combo_2" for j in build_combos(q))

def test_p1516_monte_carlo():
    assert "approved" in monte_carlo([.01,-.002,.004,.003,.005,-.001,.006,.002])
