from app.mind.p5_6d1_market_price_dedup_validator import run_p56d1_healthcheck

def test_healthcheck():
    assert run_p56d1_healthcheck()["status"]=="P5.6D1_READY"
