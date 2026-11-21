import copy
import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, FeatureFrame

def _state():
    executor = PaperPortfolioExecutor()
    signal = PaperSignal(ts=100, symbol="XAUUSD", specialist_id="S1", side="BUY", confidence=0.9, reason="TEST")
    assert executor.on_signal(signal, 100) is not None
    return executor.export_state()

@pytest.mark.parametrize("position_id,seq", [
    ("PAPER_000002", 1),
    ("PAPER_000000", 1),
    ("BROKER_000001", 1),
    ("PAPER_ABCDEF", 1),
])
def test_invalid_restored_open_id_rejected(position_id, seq):
    state = _state()
    state["positions"][0]["position_id"] = position_id
    state["seq"] = seq
    with pytest.raises(ValueError, match="INVALID_PAPER_EXECUTOR_SEQUENCE"):
        PaperPortfolioExecutor.restore_state(state)

def test_duplicate_closed_id_rejected():
    state = _state()
    pos = state["positions"].pop()
    pos["status"] = "CLOSED"
    entry = {"position": pos, "exit": 106.0, "pnl": 0.06, "close_ts": 100}
    state["closed"] = [copy.deepcopy(entry), copy.deepcopy(entry)]
    state["seq"] = 2
    with pytest.raises(ValueError, match="INVALID_PAPER_EXECUTOR_CLOSED_POSITION"):
        PaperPortfolioExecutor.restore_state(state)

def test_valid_closed_position_roundtrip():
    executor = PaperPortfolioExecutor()
    signal = PaperSignal(ts=100, symbol="XAUUSD", specialist_id="S1", side="BUY", confidence=0.9, reason="TEST")
    executor.on_signal(signal, 100)
    frame = FeatureFrame(ts=120, symbol="XAUUSD", mid=106, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)
    executor.mark_to_market(frame)
    state = executor.export_state()
    assert PaperPortfolioExecutor.restore_state(state).export_state() == state
