import json
from pathlib import Path
from tools.p2383c2_risk_normalization_repair import run

def test_p2383c2_outputs_and_samples():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    previous=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C_FIX_DATASET_DATETIME_PARSER_20260624_135953")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C2_RISK_NORMALIZATION_REPAIR_20260624_140637")

    s=run(str(dataset),str(previous),str(out))

    required=[
        "de40_oos_atr_dataset_audit.csv",
        "de40_oos_atr_all_signals.csv",
        "de40_oos_atr_timeframe_results.csv",
        "de40_oos_atr_promoted.csv",
        "de40_oos_atr_rejected.csv",
        "de40_oos_atr_outliers_clipped.csv",
        "de40_oos_atr_regime_stability.csv",
        "de40_oos_atr_session_stability.csv",
        "de40_oos_atr_footprint_stability.csv",
        "de40_oos_atr_lifecycle_stability.csv",
        "de40_oos_atr_timeframe_stability.csv",
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

def test_r_scale_is_bounded():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C2_RISK_NORMALIZATION_REPAIR_20260624_140637")
    path=out/"de40_oos_atr_all_signals.csv"
    txt=path.read_text(encoding="utf-8").splitlines()
    assert len(txt) > 1

    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["max_abs_r"] == 10.0
    assert data["original_p2382_edge_certified"] is False
    assert data["next_required"]=="P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR"
