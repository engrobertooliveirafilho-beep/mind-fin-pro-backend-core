from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import (
    classify_lifecycle,
    context_score,
)


def test_sweep_lifecycle_does_not_depend_on_future_context():
    event = {"event_type": "LIQUIDITY_SWEEP_REVERSAL_UP", "direction": "BUY_INFERRED"}
    favorable = {"post_mfe_atr": 5, "post_mae_atr": 0.1, "post_efficiency": 50, "post_followthrough": "CONTINUATION"}
    adverse = {"post_mfe_atr": 0.1, "post_mae_atr": 5, "post_efficiency": 0.02, "post_followthrough": "NO_FOLLOW"}
    assert classify_lifecycle(event, favorable) == classify_lifecycle(event, adverse)
    assert classify_lifecycle(event)["lifecycle"] == "LIQUIDITY_SWEEP_OBSERVED"


def test_displacement_lifecycle_uses_event_time_body_only():
    event = {"event_type": "INSTITUTIONAL_DISPLACEMENT_UP", "direction": "BUY_INFERRED", "body_atr": 1.1}
    assert classify_lifecycle(event)["lifecycle"] == "DISPLACEMENT_OBSERVED"


def test_context_score_ignores_future_context_fields():
    event = {"tick_volume_ratio_50": 2.0, "body_atr": 1.0, "range_atr": 2.0}
    favorable = {"post_mfe_atr": 8, "post_mae_atr": 0.1, "post_efficiency": 80}
    adverse = {"post_mfe_atr": 0.1, "post_mae_atr": 8, "post_efficiency": 0.01}
    assert context_score(80, 60, event, favorable) == context_score(80, 60, event, adverse)


def test_context_score_uses_only_observable_event_features():
    base = {"tick_volume_ratio_50": 1.0, "body_atr": 0.5, "range_atr": 1.0}
    stronger = {"tick_volume_ratio_50": 2.0, "body_atr": 1.0, "range_atr": 2.0}
    assert context_score(50, 50, stronger) > context_score(50, 50, base)


def test_unknown_event_fails_to_unclassified():
    result = classify_lifecycle({"event_type": "UNKNOWN", "direction": "NONE"})
    assert result["lifecycle"] == "UNCLASSIFIED"
    assert result["lifecycle_score"] == 0


def test_lifecycle_output_marks_event_time_scope():
    result = classify_lifecycle({"event_type": "LIQUIDITY_SWEEP", "direction": "BUY_INFERRED"})
    assert result["lifecycle_evidence"] == "EVENT_TIME_ONLY"