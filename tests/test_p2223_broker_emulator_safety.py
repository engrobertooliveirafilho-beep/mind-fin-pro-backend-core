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
    monkeypatch.setattr("app.runtime.p2223_broker_emulator.random.uniform", lambda a, b: -10000.0)
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
