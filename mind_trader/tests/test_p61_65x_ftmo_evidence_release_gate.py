from app.p61_65x_ftmo_evidence_release_gate.engine import run, p61_backtest_factory, p62_validation_lab, p65_release_gate

def test_p61_backtest_factory():
    jobs=p61_backtest_factory()
    assert isinstance(jobs,list)

def test_p62_validation_blocks_live():
    r=p62_validation_lab([{"job_id":"x","dataset":"d","asset":"A","timeframe":"H1","family":"trend"}])
    assert r[0]["REAL_ORDERS"]=="FORBIDDEN"

def test_p65_release_gate_blocks_real_ftmo():
    g=p65_release_gate([])
    assert g["FTMO_REAL"]=="FORBIDDEN"
    assert g["FTMO_REAL_RELEASE"]=="BLOCKED_INSUFFICIENT_EVIDENCE"

def test_p61_65_master_runtime():
    r=run()
    assert r["STATUS"]=="P61_65X_FTMO_EVIDENCE_AND_RELEASE_GATE_IMPLEMENTED"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
    assert r["FTMO_REAL"]=="FORBIDDEN"
