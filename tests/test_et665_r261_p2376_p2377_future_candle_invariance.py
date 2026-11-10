"""R261 source-import metamorphic regression: expected FAIL until P2377 causal fix.
No broker, terminal, filesystem writes, network or paid service.
"""
from app.runtime.p2376_de40_big_player_context_xray_engine import context_window
from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import classify_lifecycle, context_score


def test_future_candle_mutation_must_not_change_paper_permission():
    candles = [{"high": 100.5, "low": 99.5, "close": 100.0} for _ in range(70)]
    event = {
        "event_index": 40,
        "event_type": "LIQUIDITY_SWEEP_REVERSAL_UP",
        "direction": "BUY_INFERRED",
        "atr14": 1.0,
        "tick_volume_ratio_50": 1.0,
        "body_atr": 0.5,
        "range_atr": 1.0,
    }
    favorable = [dict(x) for x in candles]
    adverse = [dict(x) for x in candles]
    for i in range(41, 61):
        favorable[i].update(high=102.0, low=99.8)
        adverse[i].update(high=100.2, low=98.0)
    assert favorable[:41] == adverse[:41]

    def permission(series):
        context = context_window(series, event)
        lifecycle = classify_lifecycle(event, context)
        score = context_score(60, lifecycle["lifecycle_score"], event, context)
        return "PAPER_CANDIDATE_ALLOWED" if score >= 70 else (
            "BLOCK_LOW_CONTEXT_SCORE" if score < 55 else "OBSERVE_ONLY"
        )

    assert permission(favorable) == permission(adverse), (
        "LOOKAHEAD LEAK: mutating only future candles changed pre-event PAPER permission"
    )
