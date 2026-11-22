import math
import pytest
from app.runtime.p2223_broker_emulator import BrokerEmulator, run_simulation


@pytest.mark.parametrize("side", ["HOLD", "buy", "", None])
def test_invalid_side_never_ticks(side, monkeypatch):
    broker = BrokerEmulator()
    monkeypatch.setattr(broker.market, "tick", lambda: pytest.fail("market tick before validation"))
    with pytest.raises(ValueError, match="P2223_INVALID_SIDE"):
        broker.execute_order(side, 1)


@pytest.mark.parametrize("volume", [0, -1, True, None, "1", math.nan, math.inf])
def test_invalid_volume_never_ticks(volume, monkeypatch):
    broker = BrokerEmulator()
    monkeypatch.setattr(broker.market, "tick", lambda: pytest.fail("market tick before validation"))
    with pytest.raises(ValueError, match="P2223_INVALID_VOLUME"):
        broker.execute_order("BUY", volume)


def test_risk_kill_latched(monkeypatch):
    broker = BrokerEmulator()
    monkeypatch.setattr(broker.market, "tick", lambda: 100.0)
    monkeypatch.setattr("app.runtime.p2223_broker_emulator.random.uniform", lambda a, b: 0.0 if a == -0.1 else -10000.0)
    first = broker.execute_order("BUY", 1)
    assert first["risk"] == "KILLED"
    with pytest.raises(RuntimeError, match="P2223_RISK_KILL_LATCHED"):
        broker.execute_order("BUY", 1)
    assert len(broker.trades) == 1


@pytest.mark.parametrize("cycles", [0, -1, True, 1.5, "5"])
def test_invalid_simulation_cycles(cycles):
    with pytest.raises(ValueError, match="P2223_INVALID_CYCLES"):
        run_simulation(cycles)


def test_simulation_never_claims_certification():
    result = run_simulation(1)
    assert result["status"] == "SIMULATION_ONLY_NOT_CERTIFIED"
    assert result["mode"] == "BROKER_EMULATOR_SIMULATION_ONLY"


def test_daily_loss_limit_latches_even_below_max_drawdown():
    from app.runtime.p2223_broker_emulator import RiskEngine
    risk = RiskEngine()
    assert risk.check(-3000) == "KILLED"
    assert risk.killed is True
    before = risk.equity
    assert risk.check(1000) == "KILLED"
    assert risk.equity == before


@pytest.mark.parametrize("bad_pnl", [math.nan, math.inf, -math.inf, True, "5"])
def test_invalid_pnl_latches_risk(bad_pnl):
    from app.runtime.p2223_broker_emulator import RiskEngine
    risk = RiskEngine()
    assert risk.check(bad_pnl) == "KILLED"
    assert risk.killed is True
    assert risk.equity == 100000


@pytest.mark.parametrize("price,slippage", [
    (math.nan, 0.0),
    (math.inf, 0.0),
    (-1.0, 0.0),
    (100.0, math.inf),
    (100.0, -101.0),
])
def test_invalid_market_execution_latches_without_trade(price, slippage, monkeypatch):
    broker = BrokerEmulator()
    monkeypatch.setattr(broker.market, "tick", lambda: price)
    monkeypatch.setattr(
        "app.runtime.p2223_broker_emulator.random.uniform",
        lambda a, b: slippage,
    )
    with pytest.raises(RuntimeError, match="P2223_INVALID_MARKET_EXECUTION"):
        broker.execute_order("BUY", 1)
    assert broker.killed and broker.risk.killed
    assert broker.trades == []
    assert broker.risk.equity == 100000


def test_independent_risk_engine_kill_prevents_market_tick(monkeypatch):
    broker = BrokerEmulator()
    broker.risk.killed = True
    monkeypatch.setattr(broker.market, "tick", lambda: pytest.fail("tick after risk kill"))
    with pytest.raises(RuntimeError, match="P2223_RISK_KILL_LATCHED"):
        broker.execute_order("BUY", 1)
    assert broker.killed
    assert broker.trades == []

@pytest.mark.parametrize("bad_pnl", [math.nan, math.inf, -math.inf, True, "bad"])
def test_invalid_execution_pnl_never_records_trade(bad_pnl, monkeypatch):
    broker = BrokerEmulator()
    monkeypatch.setattr(broker.market, "tick", lambda: 100.0)
    calls = iter([0.0, bad_pnl])
    monkeypatch.setattr("app.runtime.p2223_broker_emulator.random.uniform", lambda a, b: next(calls))
    with pytest.raises(RuntimeError, match="P2223_INVALID_EXECUTION_PNL"):
        broker.execute_order("BUY", 1)
    assert broker.trades == []
    assert broker.risk.equity == 100000
    assert broker.killed and broker.risk.killed

def test_risk_equity_overflow_is_atomic_and_latched():
    from app.runtime.p2223_broker_emulator import RiskEngine
    risk = RiskEngine()
    initial_equity = risk.equity
    assert risk.check(1e308) == "OK"
    previous_equity = risk.equity
    assert math.isfinite(previous_equity)
    assert risk.check(1e308) == "KILLED"
    assert risk.killed is True
    assert risk.equity == previous_equity
    assert math.isfinite(risk.equity)
    assert risk.check(-100) == "KILLED"
    assert risk.equity == previous_equity
