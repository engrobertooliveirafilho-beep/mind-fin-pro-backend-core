from app.p39_60x_institutional_quant_os.engine import run, p48_self_healing_runtime, p60_autonomous_quant_os

def test_p39_60_self_healing_blocks_live():
    r=p48_self_healing_runtime()
    assert r["LIVE"]=="FORBIDDEN"
    assert r["REAL_ORDERS"]=="FORBIDDEN"

def test_p39_60_autonomous_quant_os():
    r=p60_autonomous_quant_os()
    assert r["mode"]=="PAPER_ONLY"
    assert r["FTMO_REAL"]=="FORBIDDEN"

def test_p39_60_master_runtime():
    r=run()
    assert r["STATUS"]=="P39_60X_INSTITUTIONAL_QUANT_OPERATING_SYSTEM_IMPLEMENTED"
    assert r["MODULES_IMPLEMENTED"]==22
    assert r["PROP_FIRM_SIMULATION"]=="READY_PAPER_ONLY"
    assert r["REAL_ORDERS"]=="FORBIDDEN"
