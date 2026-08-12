import json
from pathlib import Path
from tools.p2383c_de40_true_out_of_sample_validation import run

def test_p2383c_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    p2382=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2382_DE40_REPLAY_AFTER_LOSS_PATCH_20260624_132257")
    p2383b=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383B_DE40_WALK_FORWARD_AGGREGATION_REPAIR_20260624_134540")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_DE40_TRUE_OUT_OF_SAMPLE_VALIDATION_20260624_135409")

    s=run(str(dataset),str(p2382),str(p2383b),str(out))

    required=[
        "de40_true_oos_all_signals.csv",
        "de40_true_oos_timeframe_results.csv",
        "de40_true_oos_regime_stability.csv",
        "de40_true_oos_timeframe_stability.csv",
        "de40_true_oos_promoted.csv",
        "de40_true_oos_rejected.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["timeframes_tested"]==7
    assert s["p2384_allowed"] is False

def test_summary_lock():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_DE40_TRUE_OUT_OF_SAMPLE_VALIDATION_20260624_135409")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"]=="NOT_CERTIFIED_ORIGINAL_EDGE"
    assert data["p2384_allowed"] is False
