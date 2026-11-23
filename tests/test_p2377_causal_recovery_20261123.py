import csv
import json
from pathlib import Path
from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import (
    build_xray_router, classify_lifecycle, context_score,
)

def test_lifecycle_ignores_future_outcome_context():
    event = {"event_type": "LIQUIDITY_SWEEP_REVERSAL_UP"}
    a = classify_lifecycle(event, {"post_mfe_atr": 8.0, "post_mae_atr": 0.0, "post_efficiency": 99.0})
    b = classify_lifecycle(event, {"post_mfe_atr": 0.0, "post_mae_atr": 8.0, "post_efficiency": 0.0})
    assert a == b
    assert a["lifecycle"] == "SWEEP_DETECTED_UNCONFIRMED"
    assert a["lifecycle_score"] == 0

def test_context_score_ignores_future_efficiency():
    event = {"tick_volume_ratio_50": 1.5, "body_atr": 0.9, "range_atr": 1.9}
    a = context_score(50, 0, event, {"post_efficiency": 99.0})
    b = context_score(50, 0, event, {"post_efficiency": 0.0})
    assert a == b

def test_router_fails_closed_and_exports_no_future_labels(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    candles = data / "DE40_M15_test.csv"
    with candles.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["time", "open", "high", "low", "close", "tick_volume"])
        w.writeheader()
        for i in range(140):
            close = 100.0 + i * 0.05
            w.writerow({"time": f"2026.11.23 10:{i%60:02d}:00", "open": close-0.1, "high": close+0.2, "low": close-0.2, "close": close, "tick_volume": 100+i})
    events = tmp_path / "events.csv"
    with events.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["symbol","timeframe","time","event_index","event_type","direction","session","tick_volume_ratio_50","body_atr","range_atr"])
        w.writeheader()
        w.writerow({"symbol":"DE40","timeframe":"M15","time":"2026.11.23 10:05:00","event_index":125,"event_type":"LIQUIDITY_SWEEP_REVERSAL_UP","direction":"BUY_INFERRED","session":"EUROPE_OPEN","tick_volume_ratio_50":1.5,"body_atr":0.9,"range_atr":1.9})
    context = tmp_path / "context.csv"
    with context.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["symbol","timeframe","time","event_index","event_type","post_mfe_atr","post_mae_atr","post_efficiency","post_followthrough"])
        w.writeheader()
        w.writerow({"symbol":"DE40","timeframe":"M15","time":"2026.11.23 10:05:00","event_index":125,"event_type":"LIQUIDITY_SWEEP_REVERSAL_UP","post_mfe_atr":10,"post_mae_atr":0,"post_efficiency":99,"post_followthrough":"CONTINUATION"})
    out = tmp_path / "out"
    summary = build_xray_router(events, context, data, out, 100)
    assert summary["paper_candidate_contexts"] == 0
    assert summary["blocked_contexts"] == 1
    assert summary["real_orders"] == "FORBIDDEN"
    router_text = (out / "de40_regime_first_xray_router_events.csv").read_text(encoding="utf-8")
    library_text = (out / "de40_institutional_context_library.csv").read_text(encoding="utf-8")
    assert "post_mfe_atr" not in router_text and "post_efficiency" not in router_text
    assert "post_mfe_atr" not in library_text and "post_efficiency" not in library_text
    saved = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert saved["paper_candidate_contexts"] == 0
