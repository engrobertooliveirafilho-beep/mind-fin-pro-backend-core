import json
from pathlib import Path
from tools.p2383_de40_walk_forward_after_patch import run

def test_p2383_outputs_exist(tmp_path):
    prev = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2382_DE40_REPLAY_AFTER_LOSS_PATCH_20260624_132257")
    out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383_DE40_WALK_FORWARD_AFTER_PATCH_20260624_133908")

    summary = run(str(prev), str(out))

    required = [
        "de40_walk_forward_windows.csv",
        "de40_walk_forward_results.csv",
        "de40_walk_forward_promoted.csv",
        "de40_walk_forward_observed.csv",
        "de40_walk_forward_rejected.csv",
        "de40_regime_stability_matrix.csv",
        "de40_session_stability_matrix.csv",
        "de40_family_stability_matrix.csv",
        "de40_footprint_stability_matrix.csv",
        "de40_lifecycle_stability_matrix.csv",
        "summary.json",
    ]

    for name in required:
        assert (out / name).exists(), name
        assert (out / name).stat().st_size > 0, name

    assert summary["mode"] == "PAPER_ONLY"
    assert summary["real_orders"] == "FORBIDDEN"
    assert summary["ftmo_real"] == "FORBIDDEN"
    assert summary["windows"] == 5
    assert summary["groups_total"] >= 1

def test_summary_json_valid():
    out = Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383_DE40_WALK_FORWARD_AFTER_PATCH_20260624_133908")
    data = json.loads((out / "summary.json").read_text(encoding="utf-8"))

    assert data["mission"] == "P2383_DE40_WALK_FORWARD_AFTER_PATCH"
    assert data["anti_overfit_audit"]["learning_during_test"] == "FORBIDDEN"
    assert data["anti_overfit_audit"]["patch_during_test"] == "FORBIDDEN"
    assert data["anti_overfit_audit"]["real_execution"] == "FORBIDDEN"
