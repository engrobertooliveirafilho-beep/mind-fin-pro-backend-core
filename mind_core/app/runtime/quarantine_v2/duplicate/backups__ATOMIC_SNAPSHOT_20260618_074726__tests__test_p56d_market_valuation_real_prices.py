from app.mind.p5_6d_market_valuation_real_prices import run_p56d_healthcheck
from app.mind.p5_6d_market_valuation_real_prices.prices import parse_price, classify_market_event

def test_healthcheck():
    assert run_p56d_healthcheck()["status"]=="P5.6D_READY"

def test_parse_price():
    assert parse_price("sold for $12,500")[0] == 12500.0

def test_classify():
    assert classify_market_event("semen straw $500")=="semen_price"
    assert classify_market_event("embryo sale $2000")=="embryo_price"
