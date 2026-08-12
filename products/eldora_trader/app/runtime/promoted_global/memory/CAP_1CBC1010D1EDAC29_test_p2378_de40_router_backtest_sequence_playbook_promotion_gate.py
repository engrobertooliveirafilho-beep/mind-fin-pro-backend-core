from app.runtime.p2378_de40_router_backtest_sequence_playbook_promotion_gate import (
    infer_context_result,
    aggregate_group,
    build_playbooks,
)


def test_infer_context_result_reaches_2r():
    row = {
        "post_mfe_atr": "3.0",
        "post_mae_atr": "1.0",
        "post_efficiency": "3.0",
    }

    out = infer_context_result(row)

    assert out["result_r_proxy"] > 0
    assert out["rr_possible_proxy"] >= 2.0


def test_aggregate_group_promotes_valid_context():
    rows = []
    for _ in range(40):
        rows.append({
            "timeframe": "M5",
            "session": "EUROPE_OPEN",
            "regime": "TREND_UP",
            "lifecycle": "INSTITUTIONAL_ENTRY_CONTINUATION",
            "event_type": "INSTITUTIONAL_DISPLACEMENT_UP",
            "recommended_families": "TREND_FOLLOWING|PULLBACK",
            "result_r_proxy": "1.0",
            "post_mfe_atr": "3.0",
            "post_mae_atr": "1.0",
            "rr_possible_proxy": "3.0",
            "context_score": "80",
        })

    out = aggregate_group(
        rows,
        ["timeframe", "session", "regime", "lifecycle", "event_type", "recommended_families"],
        min_samples=30,
    )

    assert out[0]["promotion_decision"] == "PROMOTE_CONTEXT"


def test_build_playbooks_returns_rows():
    rows = []
    for _ in range(35):
        rows.append({
            "timeframe": "M5",
            "session": "EUROPE_OPEN",
            "regime": "TREND_UP",
            "lifecycle": "INSTITUTIONAL_ENTRY_CONTINUATION",
            "event_type": "INSTITUTIONAL_DISPLACEMENT_UP",
            "recommended_families": "TREND_FOLLOWING|PULLBACK",
            "result_r_proxy": "1.0",
            "post_mfe_atr": "3.0",
            "post_mae_atr": "1.0",
            "rr_possible_proxy": "3.0",
        })

    playbooks = build_playbooks(rows)

    assert len(playbooks) >= 2
    assert playbooks[0]["samples"] >= 35
