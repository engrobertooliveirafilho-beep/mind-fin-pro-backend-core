import json
from pathlib import Path
from tools.p2383b_de40_walk_forward_aggregation_repair import run

def test_p2383b_outputs():
    p2382 = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2382_DE40_REPLAY_AFTER_LOSS_PATCH_20260624_132257")
    p2383 = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383_DE40_WALK_FORWARD_AFTER_PATCH_20260624_133908")
    out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383B_DE40_WALK_FORWARD_AGGREGATION_REPAIR_20260624_134540")

    summary = run(str(p2382), str(p2383), str(out))

    required = [
        "de40_walk_forward_aggregation_results.csv",
        "de40_walk_forward_aggregation_promoted.csv",
        "de40_walk_forward_aggregation_observed.csv",
        "de40_walk_forward_aggregation_rejected.csv",
        "de40_walk_forward_aggregation_level_summary.csv",
        "summary.json",
    ]

    for f in required:
        p = out / f
        assert p.exists(), f
        assert p.stat().st_size > 0, f

    assert summary["mode"] == "PAPER_ONLY"
    assert summary["real_orders"] == "FORBIDDEN"
    assert summary["ftmo_real"] == "FORBIDDEN"
    assert summary["total_results"] > 0

def test_p2384_gate_is_boolean():
    out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383B_DE40_WALK_FORWARD_AGGREGATION_REPAIR_20260624_134540")
    data = json.loads((out / "summary.json").read_text(encoding="utf-8"))

    assert isinstance(data["p2384_allowed"], bool)
    assert data["certification"] in ["NOT_CERTIFIED", "PROMOTED_AGGREGATIONS_FOUND"]
    assert data["safety"] == "PAPER_ONLY_ONLY_REAL_ORDERS_FORBIDDEN"
