import math
import pytest
from app.runtime.p2227_2229_advanced_layer import CrisisEngine, MacroMarketTwin, StrategyEcoSystem, run

@pytest.mark.parametrize("cycles", [0, -1, True, 1.5, "2", 10001])
def test_reject_invalid_cycles(cycles):
    with pytest.raises(ValueError, match="P2227_INVALID_CYCLES"):
        run(cycles)

@pytest.mark.parametrize("price", [0, -1, True, math.nan, math.inf, "100"])
def test_crisis_reject_invalid_price(price):
    with pytest.raises(ValueError, match="P2227_INVALID_PRICE"):
        CrisisEngine().simulate_crisis(price)

def test_macro_updates_atomically(monkeypatch):
    twin = MacroMarketTwin()
    initial = dict(twin.world)
    seq = iter([0.1, math.nan, 0.1])
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.uniform", lambda a, b: next(seq))
    with pytest.raises(RuntimeError, match="P2228_INVALID_MACRO_SHOCK"):
        twin.step()
    assert twin.world == initial

def test_strategy_snapshots_and_atomic_mutations(monkeypatch):
    eco = StrategyEcoSystem()
    seq = iter([1.0, math.nan, 1.0])
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.uniform", lambda a, b: next(seq))
    with pytest.raises(RuntimeError, match="P2229_INVALID_MUTATION"):
        eco.evolve({"VOLATILITY": 20})
    assert all(s["score"] == 50 for s in eco.strategies)
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.uniform", lambda a, b: 1.0)
    old = eco.evolve({"VOLATILITY": 20})
    snapshot = [dict(s) for s in old]
    eco.evolve({"VOLATILITY": 20})
    assert old == snapshot

@pytest.mark.parametrize("bad", [{}, {"VOLATILITY": math.nan}, {"VOLATILITY": True}, None])
def test_strategy_reject_invalid_macro(bad):
    with pytest.raises(ValueError, match="P2229_INVALID_MACRO_SIGNAL"):
        StrategyEcoSystem().evolve(bad)

def test_run_is_simulation_only():
    result = run(2)
    assert result["status"] == "SIMULATION_ONLY_NOT_CERTIFIED"
    assert result["mode"] == "ADVANCED_SIMULATION_LAYER"
