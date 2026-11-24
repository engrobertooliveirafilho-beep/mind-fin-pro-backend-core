import pytest

from app.runtime.p2379_p2380_event_time_lineage_gate import (
    resolve_next_bar_entry,
    validate_event_bound_signal,
)


def valid_signal():
    return {
        "symbol": "GER40", "timeframe": "M15",
        "event_time": "2026-11-23T10:00:00+00:00", "event_index": 4,
        "event_id": "P2376_EVT_0004",
        "source_dataset_sha256": "a" * 64, "source_row_sha256": "b" * 64,
        "direction": "BUY_INFERRED",
        "entry_time": "2026-11-23T10:15:00+00:00", "entry_index": 5,
        "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN",
    }


def test_valid_event_bound_paper_signal_passes():
    assert validate_event_bound_signal(valid_signal()) == (True, "EVENT_LINEAGE_VALID_PAPER_ONLY")


def test_missing_source_hash_fails_closed():
    signal = valid_signal(); signal["source_row_sha256"] = ""
    ok, reason = validate_event_bound_signal(signal)
    assert not ok and reason.startswith("MISSING_LINEAGE:")


def test_malformed_dataset_hash_fails_closed():
    signal = valid_signal(); signal["source_dataset_sha256"] = "not-a-sha256"
    assert validate_event_bound_signal(signal) == (False, "DATASET_HASH_INVALID")


def test_entry_at_event_timestamp_is_rejected():
    signal = valid_signal(); signal["entry_time"] = signal["event_time"]
    assert validate_event_bound_signal(signal) == (False, "ENTRY_NOT_AFTER_EVENT_TIME")


def test_entry_index_must_follow_event_index():
    signal = valid_signal(); signal["entry_index"] = signal["event_index"]
    assert validate_event_bound_signal(signal) == (False, "ENTRY_MUST_BE_IMMEDIATE_NEXT_BAR")


def test_non_paper_mode_is_rejected():
    signal = valid_signal(); signal["mode"] = "LIVE"
    assert validate_event_bound_signal(signal) == (False, "EXECUTION_MODE_FORBIDDEN")


def test_resolves_exact_next_bar_only():
    candles = [
        {"symbol": "GER40", "timeframe": "M15", "time": f"2026-11-23T{hour:02d}:{minute:02d}:00+00:00"}
        for hour, minute in [(9, 0), (9, 15), (9, 30), (9, 45), (10, 0), (10, 15)]
    ]
    assert resolve_next_bar_entry(valid_signal(), candles) == 5


def test_rejects_skipped_bars():
    signal = valid_signal(); signal["entry_index"] = 6
    signal["entry_time"] = "2026-11-23T10:30:00+00:00"
    candles = [{"time": "2026-11-23T09:59:00+00:00"}, {"time": "2026-11-23T10:15:00+00:00"}]
    with pytest.raises(ValueError, match="ENTRY_MUST_BE_IMMEDIATE_NEXT_BAR"):
        resolve_next_bar_entry(signal, candles)


def test_rejects_event_bar_timestamp_mismatch():
    candles = [
        {"symbol": "GER40", "timeframe": "M15",
         "time": f"2026-11-23T{hour:02d}:{minute:02d}:00+00:00"}
        for hour, minute in [(9, 0), (9, 15), (9, 30), (9, 45), (10, 1), (10, 15)]
    ]
    with pytest.raises(ValueError, match="EVENT_BAR_TIMESTAMP_MISMATCH"):
        resolve_next_bar_entry(valid_signal(), candles)


def test_rejects_missing_next_bar():
    with pytest.raises(ValueError, match="NEXT_BAR_UNAVAILABLE"):
        resolve_next_bar_entry(valid_signal(), [{"time": "2026-11-23T10:00:00+00:00"}])

@pytest.mark.parametrize("row_index", [4, 3])
def test_authenticated_row_position(row_index):
    import hashlib
    from app.runtime.p2379_p2380_event_time_lineage_gate import resolve_verified_next_bar_entry
    signal = valid_signal()
    candles = [
        {"symbol": "GER40", "timeframe": "M15",
         "time": f"2026-11-23T{hour:02d}:{minute:02d}:00+00:00"}
        for hour, minute in [(9, 0), (9, 15), (9, 30), (9, 45), (10, 0), (10, 15)]
    ]
    rows = [c["time"].encode() for c in candles]
    dataset = b"time\n" + b"\n".join(rows) + b"\n"
    row = rows[row_index]
    signal["source_dataset_sha256"] = hashlib.sha256(dataset).hexdigest()
    signal["source_row_sha256"] = hashlib.sha256(row).hexdigest()
    if row_index == 4:
        assert resolve_verified_next_bar_entry(signal, candles, dataset, row) == 5
    else:
        with pytest.raises(ValueError, match="SOURCE_ROW_EVENT_INDEX_MISMATCH"):
            resolve_verified_next_bar_entry(signal, candles, dataset, row)

def test_p2380_positive_feedback_cannot_promote():
    from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import aggregate
    rows = [{"family": "fixture", "realized_r": 2.0 if i < 35 else -1.0}
            for i in range(40)]
    result = aggregate(rows, ["family"])
    assert len(result) == 1
    assert result[0]["profit_factor"] == 14.0
    assert result[0]["feedback_decision"] == "OBSERVE_AFTER_FEEDBACK"

def test_p2380_atr_precedes_entry(monkeypatch):
    from app.runtime import p2380_de40_forward_paper_feedback_loop_and_pnl_tracking as motor
    candles = [{"time": str(i), "open": 100.0, "close": 100.0,
                "high": 100.1, "low": 99.9} for i in range(20)]
    candles[15]["close"] = 100.2
    monkeypatch.setattr(motor, "index_for_signal", lambda *args: 15)
    calls = []
    def prior_atr(bars, index, period):
        calls.append(index)
        return 1.0
    monkeypatch.setattr(motor, "atr", prior_atr)
    result = motor.simulate_feedback({"direction": "BUY", "timeframe": "M15"}, candles)
    assert calls == [14]
    assert result["entry_price"] == 100.0

@pytest.mark.parametrize("direction,opening,high,low,policy,expected", [
    ("BUY", 100, 104, 98, "RR_3", -1.0),
    ("SELL", 100, 102, 96, "RR_3", -1.0),
    ("BUY", 97, 98, 96, "RR_3", -3.0),
    ("BUY", 102, 104, 101, "RR_3", 2.0),
])
def test_p2380_intrabar_conservative(monkeypatch, direction, opening, high, low, policy, expected):
    from app.runtime import p2380_de40_forward_paper_feedback_loop_and_pnl_tracking as motor
    candles = [{"time": str(i), "open": 100.0, "close": 100.0,
                "high": 100.1, "low": 99.9} for i in range(17)]
    candles[16].update(open=opening, high=high, low=low, close=opening)
    monkeypatch.setattr(motor, "index_for_signal", lambda *args: 15)
    monkeypatch.setattr(motor, "atr", lambda *args: 1.0)
    result = motor.simulate_feedback({"direction": direction, "timeframe": "M15",
                                      "rr_policy": policy}, candles)
    assert result["realized_r"] == expected
