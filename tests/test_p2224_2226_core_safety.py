import pytest
from app.runtime.p2224_2226_institutional_core import run, StrategyEvolutionEngine

@pytest.mark.parametrize("cycles", [0, -1, True, 1.5, "3"])
def test_invalid_cycles_fail_closed(cycles):
    with pytest.raises(ValueError, match="P2224_INVALID_CYCLES"):
        run(cycles)

def test_simulation_never_claims_certification():
    result = run(1)
    assert result["status"] == "SIMULATION_ONLY_NOT_CERTIFIED"

def test_strategy_snapshots_are_not_live_aliases(monkeypatch):
    monkeypatch.setattr("app.runtime.p2224_2226_institutional_core.random.uniform", lambda a, b: 1.0)
    engine = StrategyEvolutionEngine()
    first = engine.evolve()
    snapshot = [dict(s) for s in first]
    engine.evolve()
    assert first == snapshot
    assert first is not engine.strategies

def test_integrated_log_preserves_first_cycle(monkeypatch):
    monkeypatch.setattr("app.runtime.p2224_2226_institutional_core.random.uniform", lambda a, b: 1.0)
    result = run(3)
    assert result["log_sample"][0]["strategies"][0]["score"] == 51.0
    assert result["final_strategies"][0]["score"] == 53.0
