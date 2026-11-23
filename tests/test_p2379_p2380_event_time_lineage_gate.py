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
    assert validate_event_bound_signal(signal) == (False, "ENTRY_NOT_AFTER_EVENT_INDEX")


def test_non_paper_mode_is_rejected():
    signal = valid_signal(); signal["mode"] = "LIVE"
    assert validate_event_bound_signal(signal) == (False, "EXECUTION_MODE_FORBIDDEN")


def test_resolves_exact_next_bar_only():
    candles = [
        {"time": f"2026-11-23T{hour:02d}:{minute:02d}:00+00:00"}
        for hour, minute in [(9, 0), (9, 15), (9, 30), (9, 45), (10, 0), (10, 15)]
    ]
    assert resolve_next_bar_entry(valid_signal(), candles) == 5


def test_rejects_skipped_bars():
    signal = valid_signal(); signal["entry_index"] = 6
    signal["entry_time"] = "2026-11-23T10:30:00+00:00"
    candles = [{"time": "2026-11-23T10:00:00+00:00"}, {"time": "2026-11-23T10:15:00+00:00"}]
    with pytest.raises(ValueError, match="ENTRY_MUST_BE_IMMEDIATE_NEXT_BAR"):
        resolve_next_bar_entry(signal, candles)


def test_rejects_event_bar_timestamp_mismatch():
    candles = [{"time": "2026-11-23T09:45:00+00:00"}, {"time": "2026-11-23T10:15:00+00:00"},
               {"time": "2026-11-23T09:59:00+00:00"}, {"time": "2026-11-23T10:15:00+00:00"},
               {"time": "2026-11-23T10:00:00+00:00"}, {"time": "2026-11-23T10:15:00+00:00"}]
    with pytest.raises(ValueError, match="EVENT_BAR_TIMESTAMP_MISMATCH"):
        resolve_next_bar_entry(valid_signal(), candles)


def test_rejects_missing_next_bar():
    with pytest.raises(ValueError, match="NEXT_BAR_UNAVAILABLE"):
        resolve_next_bar_entry(valid_signal(), [{"time": "2026-11-23T10:00:00+00:00"}])