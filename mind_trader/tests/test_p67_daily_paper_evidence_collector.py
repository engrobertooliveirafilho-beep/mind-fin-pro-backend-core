from app.p67_daily_paper_evidence_collector.engine import run, simulate_day

def test_p67_simulate_day_blocks_live():
    r=simulate_day(1)
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["FTMO_REAL"]=="FORBIDDEN"

def test_p67_daily_collector():
    r=run(1)
    assert r["STATUS"]=="P67_DAILY_PAPER_EVIDENCE_COLLECTOR_IMPLEMENTED"
    assert r["REAL_BROKER"]=="DISABLED"
