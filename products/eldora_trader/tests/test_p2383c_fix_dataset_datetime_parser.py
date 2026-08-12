import json
from pathlib import Path
from tools.p2383c_fix_dataset_datetime_parser import run

def test_parser_fix_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    invalid_prev=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_DE40_TRUE_OUT_OF_SAMPLE_VALIDATION_20260624_135409")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_FIX_DATASET_DATETIME_PARSER_20260624_135953")

    s=run(str(dataset),str(invalid_prev),str(out))

    required=[
        "de40_oos_fixed_dataset_audit.csv",
        "de40_oos_fixed_all_signals.csv",
        "de40_oos_fixed_timeframe_results.csv",
        "de40_oos_fixed_promoted.csv",
        "de40_oos_fixed_rejected.csv",
        "de40_oos_fixed_regime_stability.csv",
        "de40_oos_fixed_session_stability.csv",
        "de40_oos_fixed_footprint_stability.csv",
        "de40_oos_fixed_lifecycle_stability.csv",
        "de40_oos_fixed_timeframe_stability.csv",
        "summary.json",
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["global_metrics"]["samples"] > 0
    assert s["timeframes_tested"] == 7
    assert s["p2384_allowed"] is False

def test_summary_certification_lock():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_FIX_DATASET_DATETIME_PARSER_20260624_135953")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["original_p2382_edge_certified"] is False
    assert data["p2384_allowed"] is False
    assert data["next_required"]=="P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR"
