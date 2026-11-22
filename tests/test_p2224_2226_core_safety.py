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

def test_book_rejects_nonpositive_bid_without_mutation(monkeypatch):
    from app.runtime.p2224_2226_institutional_core import OrderBookSimulator
    book = OrderBookSimulator()
    monkeypatch.setattr("app.runtime.p2224_2226_institutional_core.random.uniform", lambda a, b: -200.0)
    with pytest.raises(RuntimeError, match="P2224_INVALID_BOOK"):
        book.update_book()
    assert (book.bid, book.ask) == (100.0, 100.2)

def test_market_rejects_negative_eurusd_atomically(monkeypatch):
    from app.runtime.p2224_2226_institutional_core import MarketDigitalTwin
    twin = MarketDigitalTwin()
    before = dict(twin.assets)
    monkeypatch.setattr("app.runtime.p2224_2226_institutional_core.random.uniform", lambda a, b: -10.0)
    with pytest.raises(RuntimeError, match="P2225_INVALID_MARKET_PRICE"):
        twin.step()
    assert twin.assets == before

def test_strategy_nan_mutation_is_atomic(monkeypatch):
    import math
    engine = StrategyEvolutionEngine()
    original = [dict(s) for s in engine.strategies]
    values = iter([1.0, math.nan, 1.0])
    monkeypatch.setattr("app.runtime.p2224_2226_institutional_core.random.uniform", lambda a, b: next(values))
    with pytest.raises(RuntimeError, match="P2226_INVALID_STRATEGY_SCORE"):
        engine.evolve()
    assert engine.strategies == original
