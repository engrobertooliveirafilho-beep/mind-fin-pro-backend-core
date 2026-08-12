from app.runtime.p2376_de40_big_player_context_xray_engine import classify_event, context_window


def test_classify_event_detects_breakout():
    candles = []
    for i in range(160):
        price = 10000 + i * 0.5
        candles.append({
            "i": i,
            "time": f"2026-01-01 09:{i%60:02d}:00",
            "open": price,
            "high": price + 2,
            "low": price - 2,
            "close": price + 0.5,
            "tick_volume": 100,
        })

    candles[150]["open"] = 10080
    candles[150]["close"] = 10130
    candles[150]["high"] = 10135
    candles[150]["low"] = 10075
    candles[150]["tick_volume"] = 300

    closes = [x["close"] for x in candles]
    ev = classify_event(candles, closes, 150)

    assert ev is not None
    assert ev["institutional_footprint"] == "INFERRED_NOT_CONFIRMED"


def test_context_window_outputs_before_after():
    candles = []
    for i in range(100):
        price = 10000 + i
        candles.append({
            "i": i,
            "time": f"2026-01-01 09:{i%60:02d}:00",
            "open": price,
            "high": price + 3,
            "low": price - 3,
            "close": price,
            "tick_volume": 100,
        })

    event = {
        "event_index": 50,
        "time": candles[50]["time"],
        "event_type": "INSTITUTIONAL_DISPLACEMENT_UP",
        "direction": "BUY_INFERRED",
        "session": "EUROPE_OPEN",
        "atr14": 5,
    }

    ctx = context_window(candles, event)
    assert "post_mfe_atr" in ctx
    assert "post_mae_atr" in ctx
    assert ctx["reverse_engineering_label"].startswith("WHAT_HAPPENED")
