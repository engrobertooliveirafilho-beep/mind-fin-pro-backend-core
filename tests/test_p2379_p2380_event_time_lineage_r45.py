import importlib.util
from pathlib import Path
import pytest

MODULE = Path(__file__).resolve().parents[1] / "app/runtime/p2379_p2380_event_time_lineage_gate.py"
spec = importlib.util.spec_from_file_location("lineage_gate", MODULE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def signal():
    return dict(symbol="EURUSD", timeframe="M5", event_time="2026-01-01T00:00:00+00:00",
                event_index=0, event_id="e1", source_dataset_sha256="a"*64,
                source_row_sha256="b"*64, direction="BUY",
                entry_time="2026-01-01T00:05:00+00:00", entry_index=1,
                mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN")

def candles():
    return [{"time": "2026-01-01T00:00:00+00:00"}, {"time": "2026-01-01T00:05:00+00:00"}]

def test_valid_next_bar():
    assert gate.validate_event_bound_signal(signal())[0]
    assert gate.resolve_next_bar_entry(signal(), candles()) == 1

@pytest.mark.parametrize("bad", [True, 1.9, "1.9", -1])
def test_noncanonical_entry_index_rejected(bad):
    s = signal()
    s["entry_index"] = bad
    assert not gate.validate_event_bound_signal(s)[0]

def test_skipped_candle_rejected():
    s = signal()
    s["entry_index"] = 2
    assert not gate.validate_event_bound_signal(s)[0]

def test_timezone_required():
    s = signal()
    s["entry_time"] = "2026-01-01T00:05:00"
    assert not gate.validate_event_bound_signal(s)[0]

@pytest.mark.parametrize("bad", [None, "invalid", 4])
def test_candle_object_rejected(bad):
    c = candles()
    c[0] = bad
    with pytest.raises(ValueError, match="CANDLE_NOT_OBJECT"):
        gate.resolve_next_bar_entry(signal(), c)

def test_no_real_orders():
    s = signal()
    s["real_orders"] = "ALLOWED"
    assert not gate.validate_event_bound_signal(s)[0]
