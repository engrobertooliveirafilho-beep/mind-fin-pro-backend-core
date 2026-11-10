"""P2377 causal-gate regression against original source import; no broker/MT5."""
from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import classify_lifecycle, context_score


def test_future_outcome_mutation_does_not_change_lifecycle_or_score():
    event = {"event_type": "LIQUIDITY_SWEEP_REVERSAL_UP", "tick_volume_ratio_50": 1, "body_atr": 0.5, "range_atr": 1}
    contexts = [
        {"post_mfe_atr": 2, "post_mae_atr": .2, "post_efficiency": 10, "post_followthrough": "CONTINUATION"},
        {"post_mfe_atr": .2, "post_mae_atr": 2, "post_efficiency": .1, "post_followthrough": "NO_FOLLOW"},
    ]
    outcomes = []
    for context in contexts:
        lc = classify_lifecycle(event, context)
        outcomes.append((lc, context_score(60, lc["lifecycle_score"], event, context)))
    assert outcomes[0] == outcomes[1]


def test_uncertified_lifecycle_has_no_positive_score():
    for kind in ("LIQUIDITY_SWEEP_REVERSAL_UP", "INSTITUTIONAL_DISPLACEMENT_UP", "HIGH_VOLUME_RANGE_EXPANSION"):
        lc = classify_lifecycle({"event_type": kind}, {"post_mfe_atr": 100000})
        assert lc["lifecycle_score"] == 0
        assert "UNCONFIRMED" in lc["lifecycle"]


def test_future_labels_do_not_enter_router_decision_features():
    from inspect import getsource
    from app.runtime.p2377_de40_regime_first_signal_router_with_xray_lifecycle import build_xray_router
    source = getsource(build_xray_router)
    assert 'permission = "BLOCK_UNCERTIFIED_CAUSAL_LIFECYCLE"' in source
    assert 'row["post_mfe_atr"]' not in source
    assert 'row["post_mae_atr"]' not in source
    assert 'row["post_efficiency"]' not in source
