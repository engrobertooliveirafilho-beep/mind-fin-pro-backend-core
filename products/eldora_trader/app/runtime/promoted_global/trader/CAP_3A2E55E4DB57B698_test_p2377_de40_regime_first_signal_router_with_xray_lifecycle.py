from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import (
    classify_lifecycle,
    recommended_families,
    context_score,
)


def test_lifecycle_sweep_reversal():
    event = {
        "event_type": "LIQUIDITY_SWEEP_REVERSAL_UP",
        "direction": "BUY_INFERRED",
    }
    context = {
        "post_mfe_atr": "1.5",
        "post_mae_atr": "0.5",
        "post_efficiency": "3.0",
        "post_followthrough": "CONTINUATION",
    }

    out = classify_lifecycle(event, context)

    assert out["lifecycle"] == "LIQUIDITY_REVERSAL_ENTRY"
    assert out["lifecycle_score"] >= 70


def test_router_recommends_pullback_for_trend():
    out = recommended_families(
        regime="TREND_UP_EXPANSION",
        lifecycle="INSTITUTIONAL_ENTRY_CONTINUATION",
        footprint="INSTITUTIONAL_DISPLACEMENT_UP",
        volatility="VOLATILITY_EXPANSION",
    )

    assert "TREND_FOLLOWING" in out["recommended_families"]
    assert "PULLBACK" in out["recommended_families"]
    assert "BREAKOUT" in out["recommended_families"]


def test_context_score_respects_bounds():
    event = {
        "tick_volume_ratio_50": "2.0",
        "body_atr": "1.0",
        "range_atr": "2.0",
    }
    context = {
        "post_efficiency": "3.0",
    }

    score = context_score(80, 85, event, context)

    assert 0 <= score <= 100
    assert score > 50
