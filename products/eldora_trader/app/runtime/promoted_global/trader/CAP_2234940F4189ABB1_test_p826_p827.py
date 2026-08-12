from mind_trader.app.engines.core import DualModeEngine, TradeIntent, ValidationProtocol, module_status

def test_modules_active():
    s=module_status()
    assert s["production"]=="BLOCKED"
    assert s["edge_claim"]=="NONE"

def test_no_stop_blocked():
    e=DualModeEngine()
    t=TradeIntent("FTMO_EVALUATION_SIMULATION_MODE","WIN","S1","trend",100,None,120,100,0,0,0,0,0)
    assert e.process_trade(t)["decision"]=="NAO_OPERAR"

def test_daily_loss_blocked():
    e=DualModeEngine()
    t=TradeIntent("FTMO_EVALUATION_SIMULATION_MODE","WIN","S1","trend",100,95,120,1000,0,-4500,0,0,0)
    assert "DAILY_LOSS_LIMIT_RISK" in e.process_trade(t)["ftmo_reason"]

def test_false_edge_rejected():
    status,detail=ValidationProtocol().validate_edge({"in_sample":True})
    assert status=="ABORTAR_PROMOÇÃO"
    assert "missing" in detail

def test_complete_validation_only_paper():
    r=dict(in_sample=True,out_of_sample=True,walk_forward=True,monte_carlo=True,slippage=True,spread=True,stress=True,ruin_risk=True)
    assert ValidationProtocol().validate_edge(r)[0]=="P8.26_READY_FOR_PAPER_TRADING"
