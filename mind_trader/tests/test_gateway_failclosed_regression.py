import pytest
from mind_trader.app.execution import gateway as gateway_module
from mind_trader.app.execution.gateway import ExecutionGateway
from mind_trader.app.engines.core import DualModeEngine, TradeIntent
from mind_trader.app.risk.ftmo_ruleset import save_default_ftmo_config

@pytest.fixture
def gateway(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = tmp_path / "ftmo.json"
    save_default_ftmo_config(str(cfg))
    g = ExecutionGateway(str(tmp_path/"exec.jsonl"), str(cfg),
                         str(tmp_path/"session.json"), str(tmp_path/"day.jsonl"),
                         str(tmp_path/"broker.jsonl"))
    g.paper.open_session()
    return g

def submit(g, **changes):
    trade = dict(symbol="WIN", strategy_id="S1", entry=100, stop=98,
                 target=104, risk_amount=500, daily_trades=1, side="BUY")
    trade.update(changes)
    return g.submit_order("PAPER", trade,
        dict(regime="TREND_UP", normalized_atr=0.005, trade_allowed=True),
        dict(genome_id="g1", regime="TREND_UP", edge_claim="NONE"))

@pytest.mark.parametrize("changes", [
    {"session_allowed":"false"}, {"news_blocked":0}, {"risk_amount":"500"},
    {"entry":float("nan")}, {"target":float("inf")}, {"open_risk":True},
    {"daily_trades":-1}, {"loss_streak":False}, {"symbol":""},
    {"strategy_id":None}, {"side":"INVALID"},
])
def test_invalid_inputs_never_route(gateway, monkeypatch, changes):
    def forbidden(*args, **kwargs):
        pytest.fail("invalid input reached broker")
    monkeypatch.setattr(gateway_module, "paper_route_order", forbidden)
    result = submit(gateway, **changes)
    assert result["decision"] == "REJECT_ORDER"
    assert result["production"] == "BLOCKED"

@pytest.mark.parametrize("reply", [
    None, {}, {"decision":"PAPER_ORDER_REJECTED_FILL"},
    {"decision":"PAPER_ORDER_ACCEPTED"},
])
def test_broker_rejection_never_becomes_acceptance(gateway, monkeypatch, reply):
    monkeypatch.setattr(gateway_module, "paper_route_order", lambda *a, **k: reply)
    r = submit(gateway)
    assert r["decision"] == "REJECT_ORDER"
    assert r["order_status"] == "SIMULATED_REJECTED"

def test_valid_paper_fill(gateway):
    r = submit(gateway)
    assert r["decision"] == "ACCEPT_SIMULATED_ORDER"
    assert r["paper_broker"]["order_status"] == "PAPER_FILLED_SIMULATED"
    assert r["real_broker_routing"] == "DISABLED"

@pytest.mark.parametrize("mode", ["FTMO_SIMULATION_MODE", "FTMO_EVALUATION_SIMULATION_MODE"])
def test_historical_modes(tmp_path, mode):
    engine = DualModeEngine(str(tmp_path))
    t = TradeIntent(mode,"WIN","S1","TREND_UP",100,98,104,500,0,0,0,0,0)
    assert engine.process_trade(t)["decision"] == "OPERAR_SIMULADO"

@pytest.mark.parametrize("mode", ["LIVE","FTMO_REAL","UNKNOWN"])
def test_legacy_forbidden_modes(tmp_path, mode):
    engine = DualModeEngine(str(tmp_path))
    t = TradeIntent(mode,"WIN","S1","TREND_UP",100,98,104,500,0,0,0,0,0)
    with pytest.raises(ValueError, match="PAPER_ONLY_MODE_REQUIRED"):
        engine.process_trade(t)
    assert not list(tmp_path.rglob("*.jsonl"))
