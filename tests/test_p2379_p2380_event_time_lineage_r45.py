import hashlib
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
    return [{"time": "2026-01-01T00:00:00+00:00", "symbol": "EURUSD", "timeframe": "M5"}, {"time": "2026-01-01T00:05:00+00:00", "symbol": "EURUSD", "timeframe": "M5"}]

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

def test_hash_verification_from_source_bytes():
    s = signal()
    dataset, row = b"header\noriginal-row\n", b"original-row"
    s["source_dataset_sha256"] = hashlib.sha256(dataset).hexdigest()
    s["source_row_sha256"] = hashlib.sha256(row).hexdigest()
    assert gate.verify_source_hashes(s, dataset, row)[0]
    assert gate.verify_source_hashes(s, dataset + b"tamper", row) == (False, "DATASET_HASH_MISMATCH")
    assert gate.verify_source_hashes(s, dataset, row + b"tamper") == (False, "ROW_HASH_MISMATCH")
    assert gate.verify_source_hashes(s, None, row) == (False, "SOURCE_BYTES_REQUIRED")

def test_verified_boundary_accepts_original_bytes():
    s = signal()
    dataset, row = b"header\noriginal-row\n", b"original-row"
    s["source_dataset_sha256"] = hashlib.sha256(dataset).hexdigest()
    s["source_row_sha256"] = hashlib.sha256(row).hexdigest()
    assert gate.resolve_verified_next_bar_entry(s, candles(), dataset, row) == 1

@pytest.mark.parametrize("dataset,row,reason", [
    (b"tampered-dataset", b"original-row", "DATASET_HASH_MISMATCH"),
    (b"header\noriginal-row\n", b"tampered-row", "ROW_HASH_MISMATCH"),
    (None, b"original-row", "SOURCE_BYTES_REQUIRED"),
])
def test_verified_boundary_fails_closed(dataset, row, reason):
    s = signal()
    s["source_dataset_sha256"] = hashlib.sha256(b"header\noriginal-row\n").hexdigest()
    s["source_row_sha256"] = hashlib.sha256(b"original-row").hexdigest()
    with pytest.raises(ValueError, match=reason):
        gate.resolve_verified_next_bar_entry(s, candles(), dataset, row)

def test_p2382_replay_without_oos_is_not_promoted():
    evidence = {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
                "ftmo_real": "FORBIDDEN", "signals_replayed": 227,
                "wins": 224, "losses": 0, "profit_factor": 999.0}
    assert gate.validate_replay_promotion(evidence) == (False, "INDEPENDENT_OOS_NOT_CERTIFIED")

def test_p2382_requires_temporal_audit_and_lineage():
    e = {"mode": "PAPER_ONLY", "real_orders": "FORBIDDEN",
         "ftmo_real": "FORBIDDEN", "independent_oos_certified": True}
    assert gate.validate_replay_promotion(e)[0] is False
    e["temporal_leakage_audit_pass"] = True
    assert gate.validate_replay_promotion(e)[0] is False
    e["source_lineage_verified"] = True
    assert gate.validate_replay_promotion(e) == (False, "EXTERNAL_OOS_EVIDENCE_VERIFIER_REQUIRED")

def test_p2382_real_orders_forbidden():
    e = {"mode": "PAPER_ONLY", "real_orders": "ALLOWED", "ftmo_real": "FORBIDDEN",
         "independent_oos_certified": True, "temporal_leakage_audit_pass": True,
         "source_lineage_verified": True}
    assert gate.validate_replay_promotion(e) == (False, "REAL_EXECUTION_FORBIDDEN")

@pytest.mark.parametrize("field,value,reason", [
    ("symbol", "GBPUSD", "CANDLE_SYMBOL_MISMATCH"),
    ("timeframe", "H1", "CANDLE_TIMEFRAME_MISMATCH"),
])
def test_candle_identity_mismatch_rejected(field, value, reason):
    c = candles()
    c[0][field] = value
    with pytest.raises(ValueError, match=reason):
        gate.resolve_next_bar_entry(signal(), c)

def test_duplicate_candle_time_rejected():
    c = candles()
    c[1]["time"] = c[0]["time"]
    with pytest.raises(ValueError, match="CANDLE_SERIES_NOT_STRICTLY_CHRONOLOGICAL"):
        gate.resolve_next_bar_entry(signal(), c)

@pytest.mark.parametrize("missing", ["symbol", "timeframe"])
def test_candle_identity_required(missing):
    c = candles()
    del c[0][missing]
    with pytest.raises(ValueError, match="CANDLE_IDENTITY_MISSING"):
        gate.resolve_next_bar_entry(signal(), c)

def test_hashed_row_must_belong_to_original_dataset():
    s = signal()
    dataset = b"header\noriginal-row\n"
    foreign_row = b"foreign-row"
    s["source_dataset_sha256"] = hashlib.sha256(dataset).hexdigest()
    s["source_row_sha256"] = hashlib.sha256(foreign_row).hexdigest()
    assert gate.verify_source_hashes(s, dataset, foreign_row) == (False, "ROW_NOT_IN_DATASET")
    with pytest.raises(ValueError, match="ROW_NOT_IN_DATASET"):
        gate.resolve_verified_next_bar_entry(s, candles(), dataset, foreign_row)


def test_paper_bus_coverage_rejects_missing_historical_signal():
    from app.runtime.p2379_p2380_event_time_lineage_gate import verify_paper_bus_coverage
    def item(n):
        return {"signal_id": n, "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"}
    ready = [item("P2379_CONTEXT_000157"), item("P2379_CONTEXT_000158")]
    assert verify_paper_bus_coverage(ready, ready[:1]) == (False, "PAPER_BUS_COVERAGE_MISMATCH")
    assert verify_paper_bus_coverage(ready, ready) == (True, "PAPER_BUS_COVERAGE_VERIFIED")
    assert verify_paper_bus_coverage(ready, ready[::-1]) == (False, "PAPER_BUS_ORDER_MISMATCH")
    assert verify_paper_bus_coverage(ready, [ready[0], ready[0]]) == (False, "PAPER_BUS_DUPLICATE_SIGNAL_ID")
    assert verify_paper_bus_coverage(ready, [item("UNEXPECTED"), ready[1]]) == (False, "PAPER_BUS_COVERAGE_MISMATCH")
    assert verify_paper_bus_coverage(ready, [{**ready[0], "real_orders": "ALLOWED"}, ready[1]]) == (False, "PAPER_BUS_EXECUTION_MODE_FORBIDDEN")
    assert verify_paper_bus_coverage([], []) == (False, "PAPER_BUS_EMPTY")
    assert verify_paper_bus_coverage(ready, [{**ready[0], "timeframe": "H1"}, ready[1]]) == (False, "PAPER_BUS_PAYLOAD_MISMATCH")


def test_paper_bus_csv_validates_original_payload_and_rejects_truncation():
    import csv
    import io
    from app.runtime.p2379_p2380_event_time_lineage_gate import validate_paper_bus_csv
    header = b"signal_id,mode,real_orders,ftmo_real,timeframe\n"
    a = b"A,PAPER_ONLY,FORBIDDEN,FORBIDDEN,M1\n"
    b = b"B,PAPER_ONLY,FORBIDDEN,FORBIDDEN,M5\n"
    assert validate_paper_bus_csv(header + a + b, header + a + b) == (True, "PAPER_BUS_COVERAGE_VERIFIED")
    assert validate_paper_bus_csv(header + a + b, header + a) == (False, "PAPER_BUS_COVERAGE_MISMATCH")
    assert validate_paper_bus_csv(header + a + b, header + b + a) == (False, "PAPER_BUS_ORDER_MISMATCH")
    assert validate_paper_bus_csv(header + a + b, header + a + b.replace(b"M5", b"H1")) == (False, "PAPER_BUS_PAYLOAD_MISMATCH")
    assert validate_paper_bus_csv(header + a + b, b"signal_id,signal_id,mode,real_orders,ftmo_real\n") == (False, "PAPER_BUS_CSV_HEADER_INVALID")
    assert validate_paper_bus_csv(header + a + b, header + a + b"B,PAPER_ONLY,FORBIDDEN\n") == (False, "PAPER_BUS_CSV_ROW_INVALID")
    assert validate_paper_bus_csv(header + a + b, b"\xff") == (False, "PAPER_BUS_CSV_INVALID")


def test_p2379_writer_preserves_all_ready_signals(tmp_path):
    import csv
    from app.runtime.p2379_de40_forward_paper_emission_from_promoted_playbooks import run
    def write(path, rows):
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["footprint", "regime", "samples", "profit_factor_proxy", "expectancy_r_proxy", "max_drawdown_r_proxy"])
            writer.writeheader()
            writer.writerows(rows)
    ready = [{"footprint": "TREND_UP", "regime": "TREND_UP", "samples": "100", "profit_factor_proxy": "2", "expectancy_r_proxy": "0.5", "max_drawdown_r_proxy": "1"}] * 505
    p = tmp_path / "playbooks.csv"
    c = tmp_path / "contexts.csv"
    s = tmp_path / "sequences.csv"
    write(p, ready)
    write(c, [])
    write(s, [])
    out = tmp_path / "out"
    result = run(p, c, s, out)
    with (out / "mind_de40_paper_signal_bus_p2379.csv").open(newline="", encoding="utf-8") as f:
        bus = list(csv.DictReader(f))
    assert result["paper_signals_ready"] == 505
    assert result["paper_signal_bus_rows"] == 505
    assert len(bus) == 505
    assert bus[-1]["signal_id"] == "P2379_PLAYBOOK_000505"


def test_p2380_blocks_unbound_context_templates(tmp_path):
    import csv
    from app.runtime.p2380_de40_forward_paper_feedback_loop_and_pnl_tracking import run
    bus = tmp_path / "bus.csv"
    with bus.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["signal_id", "symbol", "timeframe", "mode", "real_orders", "ftmo_real"])
        writer.writeheader()
        writer.writerow({"signal_id": "P2379_PLAYBOOK_000001", "symbol": "DE40", "timeframe": "M5", "mode": "PAPER_ONLY", "real_orders": "FORBIDDEN", "ftmo_real": "FORBIDDEN"})
    with pytest.raises(ValueError, match="P2380_UNVERIFIED_EVENT_LINEAGE"):
        run(bus, tmp_path, tmp_path / "out")
