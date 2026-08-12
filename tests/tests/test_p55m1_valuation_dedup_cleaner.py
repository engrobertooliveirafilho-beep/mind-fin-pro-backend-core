from app.mind.p5_5m1_valuation_dedup_cleaner import run_p55m1_healthcheck

def test_p55m1_healthcheck():
    assert run_p55m1_healthcheck()["status"]=="P5.5M1_READY"
