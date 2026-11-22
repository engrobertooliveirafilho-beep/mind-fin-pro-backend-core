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

def test_crisis_rejects_unknown_event(monkeypatch):
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.choice", lambda choices: "UNSUPPORTED")
    with pytest.raises(RuntimeError, match="P2227_INVALID_CRISIS_EVENT"):
        CrisisEngine().simulate_crisis(100.0)

def test_crisis_rejects_price_that_rounds_to_zero(monkeypatch):
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.choice", lambda choices: "NONE")
    with pytest.raises(RuntimeError, match="P2227_INVALID_CRISIS_PRICE"):
        CrisisEngine().simulate_crisis(0.001)

def test_crisis_rejects_nan_shock(monkeypatch):
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.choice", lambda choices: "CRASH")
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.uniform", lambda a, b: math.nan)
    with pytest.raises(RuntimeError, match="P2227_INVALID_CRISIS_SHOCK"):
        CrisisEngine().simulate_crisis(100.0)

@pytest.mark.parametrize("event,bad", [("CRASH", -0.1), ("CRASH", 0.9), ("SPIKE", -0.1), ("SPIKE", 0.9), ("LIQUIDITY_DRAIN", 0.9), ("CRASH", True), ("SPIKE", "0.1"), ("LIQUIDITY_DRAIN", float("inf"))])
def test_crisis_shock_bounds_fail_closed(monkeypatch, event, bad):
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.choice", lambda choices: event)
    monkeypatch.setattr("app.runtime.p2227_2229_advanced_layer.random.uniform", lambda a, b: bad)
    with pytest.raises(RuntimeError, match="P2227_INVALID_CRISIS_SHOCK"):
        CrisisEngine().simulate_crisis(100.0)
