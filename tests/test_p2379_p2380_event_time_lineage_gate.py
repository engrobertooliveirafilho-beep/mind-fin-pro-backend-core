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

@pytest.mark.parametrize("gross,risk,spread,slippage,commission,expected", [
    (2, 10, 1, 0.5, 1, 1.7),
    (-1, 10, 1, 0.5, 1, -1.3),
    (0, 10, 0, 0, 0, 0),
    (1, 0, 1, 0, 0, None),
    (1, 10, -1, 0, 0, None),
    (1, 10, float("nan"), 0, 0, None),
])
def test_p2380_execution_costs(gross,risk,spread,slippage,commission,expected):
    from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import apply_execution_costs
    kwargs = dict(spread_points=spread, slippage_points_per_side=slippage,
                  commission_points_round_trip=commission)
    if expected is None:
        with pytest.raises(ValueError, match="P2380_COST_INPUT_INVALID"):
            apply_execution_costs(gross,risk,**kwargs)
    else:
        result = apply_execution_costs(gross,risk,**kwargs)
        assert result["realized_r"] == pytest.approx(expected)

def test_p2380_integrated_costs(monkeypatch):
    from app.runtime import p2380_de40_forward_paper_feedback_loop_and_pnl_tracking as motor
    candles = [{"time": str(i), "open": 100.0, "close": 100.0,
                "high": 100.1, "low": 99.9} for i in range(17)]
    candles[15].update(high=104, low=98)
    monkeypatch.setattr(motor, "index_for_signal", lambda *args: 15)
    monkeypatch.setattr(motor, "atr", lambda *args: 1.0)
    signal = {"direction": "BUY", "timeframe": "M15", "rr_policy": "RR_3"}
    result = motor.simulate_feedback(signal, candles, execution_costs={
        "spread_points": 0.1, "slippage_points_per_side": 0.05,
        "commission_points_round_trip": 0.1})
    assert result["gross_r"] == -1.0
    assert result["cost_r"] == pytest.approx(0.3)
    assert result["realized_r"] == pytest.approx(-1.3)
    assert result["costs_applied"] is True

@pytest.mark.parametrize("fault", ["none", "digest", "ohlc", "chronology", "identity"])
def test_p2380_authenticated_csv(fault):
    import hashlib
    from app.runtime.p2379_p2380_event_time_lineage_gate import parse_verified_replay_source
    row = b"DE40,M15,2026-01-01T10:00:00+00:00,100,102,99,101"
    following = b"DE40,M15,2026-01-01T10:15:00+00:00,101,103,100,102"
    if fault == "ohlc":
        following = following.replace(b",103,", b",98,")
    if fault == "chronology":
        following = following.replace(b"10:15", b"10:00")
    if fault == "identity":
        following = following.replace(b"DE40", b"EURUSD")
    payload = b"symbol,timeframe,time,open,high,low,close\n" + row + b"\n" + following + b"\n"
    digest = hashlib.sha256(payload).hexdigest()
    signal = dict(symbol="DE40", timeframe="M15", event_id="fixture",
                  event_index=0, entry_index=1, event_time="2026-01-01T10:00:00+00:00",
                  entry_time="2026-01-01T10:15:00+00:00", direction="BUY",
                  source_dataset_sha256=digest, source_row_sha256=hashlib.sha256(row).hexdigest(),
                  mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN")
    trusted = "0" * 64 if fault == "digest" else digest
    if fault == "none":
        candles, idx = parse_verified_replay_source(signal, payload, trusted_dataset_sha256=trusted)
        assert idx == 1 and candles[idx]["open"] == 101.0
    else:
        errors = {"digest": "TRUSTED_DATASET_HASH_MISMATCH", "ohlc": "REPLAY_OHLC_INVALID",
                  "chronology": "REPLAY_CHRONOLOGY_INVALID", "identity": "REPLAY_CANDLE_IDENTITY_MISMATCH"}
        with pytest.raises(ValueError, match=errors[fault]):
            parse_verified_replay_source(signal, payload, trusted_dataset_sha256=trusted)

@pytest.mark.parametrize("fault", ["none", "short_window", "missing_costs"])
def test_p2380_verified_executor(fault):
    import hashlib
    from datetime import datetime, timedelta, timezone
    from app.runtime import p2380_de40_forward_paper_feedback_loop_and_pnl_tracking as motor
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    count = 16 if fault == "short_window" else 15 + motor.hold_for_timeframe("M15")
    rows = []
    for i in range(count):
        stamp = (start + timedelta(minutes=15*i)).isoformat()
        rows.append(f"DE40,M15,{stamp},100,101,99,100".encode())
    payload = b"symbol,timeframe,time,open,high,low,close\n" + b"\n".join(rows) + b"\n"
    digest = hashlib.sha256(payload).hexdigest()
    signal = dict(symbol="DE40", timeframe="M15", event_id="fixture-14",
                  event_index=14, entry_index=15,
                  event_time=(start+timedelta(minutes=210)).isoformat(),
                  entry_time=(start+timedelta(minutes=225)).isoformat(),
                  direction="BUY", rr_policy="RR_3", source_dataset_sha256=digest,
                  source_row_sha256=hashlib.sha256(rows[14]).hexdigest(),
                  mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN")
    costs = None if fault == "missing_costs" else dict(spread_points=0.2,
        slippage_points_per_side=0.1, commission_points_round_trip=0.2)
    if fault != "none":
        reason = "P2380_REPLAY_WINDOW_INCOMPLETE" if fault == "short_window" else "P2380_EXECUTION_COSTS_REQUIRED"
        with pytest.raises(ValueError, match=reason):
            motor.simulate_verified_feedback(signal, payload, trusted_dataset_sha256=digest, execution_costs=costs)
    else:
        result = motor.simulate_verified_feedback(signal, payload, trusted_dataset_sha256=digest, execution_costs=costs)
        assert result["entry_index"] == 15
        assert result["source_dataset_sha256"] == digest
        assert result["costs_applied"] is True
        assert result["realized_r"] == pytest.approx(result["gross_r"]-result["cost_r"], abs=1e-6)
        assert result["mode"] == "PAPER_ONLY"


@pytest.mark.parametrize("fault", ["none", "missing_timezone", "wrong_offset"])
def test_p2380_mt5_source_timezone(fault):
    import hashlib
    from datetime import datetime, timedelta, timezone
    from app.runtime import p2380_de40_forward_paper_feedback_loop_and_pnl_tracking as motor
    tz = timezone(timedelta(hours=2))
    start = datetime(2026, 1, 1, tzinfo=tz)
    rows = []
    for i in range(15 + motor.hold_for_timeframe("M15")):
        stamp = (start + timedelta(minutes=15*i)).strftime("%Y.%m.%d %H:%M:%S")
        rows.append(f"{stamp};100;101;99;100;10;120;0;DE40;M15".encode())
    payload = b"time;open;high;low;close;tick_volume;spread;real_volume;symbol;timeframe\r\n" + b"\r\n".join(rows) + b"\r\n"
    digest = hashlib.sha256(payload).hexdigest()
    signal = dict(symbol="DE40", timeframe="M15", event_id="mt5-fixture",
                  event_index=14, entry_index=15,
                  event_time=(start+timedelta(minutes=210)).isoformat(),
                  entry_time=(start+timedelta(minutes=225)).isoformat(),
                  direction="BUY", rr_policy="RR_3", source_dataset_sha256=digest,
                  source_row_sha256=hashlib.sha256(rows[14]).hexdigest(),
                  mode="PAPER_ONLY", real_orders="FORBIDDEN", ftmo_real="FORBIDDEN")
    costs = dict(spread_points=0.2, slippage_points_per_side=0.1, commission_points_round_trip=0.2)
    supplied = None if fault == "missing_timezone" else timezone.utc if fault == "wrong_offset" else tz
    kwargs = dict(trusted_dataset_sha256=digest, execution_costs=costs, source_timezone=supplied)
    if fault == "none":
        result = motor.simulate_verified_feedback(signal, payload, **kwargs)
        assert result["entry_index"] == 15
        assert result["costs_applied"] is True
    else:
        with pytest.raises(ValueError):
            motor.simulate_verified_feedback(signal, payload, **kwargs)
