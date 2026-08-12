from app.runtime.p2381_de40_loss_lesson_auto_patch_and_memory_graph import (
    classify_loss,
    aggregate_loss,
    decay_playbooks,
)


def test_classify_loss_immediate_adverse():
    row = {
        "realized_r": "-1",
        "mae_r": "1.2",
        "mfe_r": "0.2",
        "rr_realized": "0.2",
        "paper_result": "STOP_LOSS",
    }

    loss_type = classify_loss(row)

    assert "IMMEDIATE_ADVERSE_MOVE" in loss_type
    assert "DIRECT_STOP_LOSS" in loss_type


def test_aggregate_loss_blocks_bad_group():
    rows = []
    for _ in range(10):
        rows.append({
            "family": "BAD",
            "timeframe": "M5",
            "realized_r": "-1",
            "mae_r": "1",
            "mfe_r": "0.2",
        })

    out = aggregate_loss(rows, ["family", "timeframe"], min_losses=5)

    assert out[0]["patch_action"] == "BLOCK"


def test_decay_playbooks_blocks_high_loss_rate():
    rows = []
    for _ in range(10):
        rows.append({
            "family": "PULLBACK",
            "timeframe": "M5",
            "session": "EUROPE_OPEN",
            "regime": "TREND_UP",
            "lifecycle": "ENTRY",
            "footprint": "DISPLACEMENT",
            "realized_r": "-1",
        })

    out = decay_playbooks(rows)

    assert out[0]["playbook_patch_decision"] == "BLOCK_PLAYBOOK"
