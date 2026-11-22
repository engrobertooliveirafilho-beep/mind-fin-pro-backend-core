import copy
import pytest
from app.runtime.p2300_proxy_mc_gate import reconcile_proxy_monte_carlo

def rows():
    return [
        dict(symbol="GER40",timeframe="H1",family=family,confirmation=confirmation,exit_model="TIME_EXIT",
             simulations="1000",trades_per_simulation="100",base_pf_from_segments="1,5246",
             worst_segment_pf="0,844",pf_mean="2,0394",pf_p10="1,5838",dd_p95="852,07",
             risk_of_ruin="0",decision="PASS_MONTE_CARLO",mode="PAPER_ONLY",real_orders="FORBIDDEN")
        for family in ("LIQUIDITY_SWEEP_REVERSAL","VWAP_REVERSION")
        for confirmation in ("MTF_REQUIRED","VOLATILITY_REQUIRED")
    ]

def test_historical_proxy_cannot_certify():
    r=reconcile_proxy_monte_carlo(rows())
    assert r["historical_passes"]==4 and r["simulations_reported"]==4000
    assert not r["robustness_certified"] and not r["promotion_allowed"]

def test_new_ledger_cannot_retroactively_certify():
    assert not reconcile_proxy_monte_carlo(rows(),trade_ledger=[1,-1])["robustness_certified"]

@pytest.mark.parametrize("key,value",[
    ("mode","LIVE"),("real_orders","ALLOWED"),("decision","APPROVE_REAL"),
    ("simulations","1"),("risk_of_ruin","NaN"),("pf_mean","inf"),
    ("dd_p95","-1"),("family","UNKNOWN")
])
def test_fail_closed(key,value):
    data=rows()
    data[0][key]=value
    with pytest.raises(ValueError):reconcile_proxy_monte_carlo(data)

def test_duplicate_strategy_rejected():
    data=rows()
    data[1]["confirmation"]="MTF_REQUIRED"
    with pytest.raises(ValueError):reconcile_proxy_monte_carlo(data)

def test_missing_row_rejected():
    with pytest.raises(ValueError):reconcile_proxy_monte_carlo(rows()[:3])
