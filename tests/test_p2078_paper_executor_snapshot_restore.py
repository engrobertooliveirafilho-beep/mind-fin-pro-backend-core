import copy
import pytest
from app.runtime.p2071_2080_realtime_paper_runtime import PaperPortfolioExecutor, PaperSignal, FeatureFrame, RuntimePersistence

def _signal(ts=100):
    return PaperSignal(ts=ts, symbol="XAUUSD", specialist_id="s1", side="BUY", confidence=0.9, reason="TEST")

def _frame(ts=120):
    return FeatureFrame(ts=ts, symbol="XAUUSD", mid=101, spread=0.2, return_1=0, volatility_20=0, body_to_range=0, rsi_14=50, stoch_14=50, close_position=0.5)

def test_restore_open_book_risk_and_clock_from_disk(tmp_path):
    original = PaperPortfolioExecutor()
    assert original.on_signal(_signal(), 100) is not None
    original.mark_to_market(_frame())
    state = original.export_state()
    store = RuntimePersistence(str(tmp_path / "snapshot.json"))
    store.save(state)
    restored = PaperPortfolioExecutor.restore_state(store.load())
    assert restored.export_state() == state
    assert restored.on_signal(_signal(110), 100) is None
    with pytest.raises(ValueError, match="OUT_OF_ORDER_PAPER_MARK"):
        restored.mark_to_market(_frame(119))

@pytest.mark.parametrize("field,value", [
    ("schema", "BROKER_REAL"),
    ("equity", float("nan")),
    ("seq", -1),
    ("risk_locked", "false"),
    ("last_event_ts", -1),
])
def test_corrupt_snapshot_rejected(field, value):
    original = PaperPortfolioExecutor()
    assert original.on_signal(_signal(), 100) is not None
    state = original.export_state()
    state[field] = value
    with pytest.raises(ValueError, match="INVALID_PAPER_EXECUTOR_STATE"):
        PaperPortfolioExecutor.restore_state(state)

def test_duplicate_specialist_rejected():
    original = PaperPortfolioExecutor()
    assert original.on_signal(_signal(), 100) is not None
    state = original.export_state()
    second = copy.deepcopy(state["positions"][0])
    second["position_id"] = "PAPER_000002"
    state["positions"].append(second)
    state["seq"] = 2
    with pytest.raises(ValueError, match="INVALID_PAPER_EXECUTOR_POSITION"):
        PaperPortfolioExecutor.restore_state(state)
