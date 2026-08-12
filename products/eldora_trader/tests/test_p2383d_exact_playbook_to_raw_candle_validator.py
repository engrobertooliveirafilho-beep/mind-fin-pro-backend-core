import json
from pathlib import Path
from tools.p2383d_exact_playbook_to_raw_candle_validator import run

def test_p2383d_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    p2378=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2378_DE40_ROUTER_BACKTEST_SEQUENCE_PLAYBOOK_PROMOTION_GATE_20260624_125449")
    p2379=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2379_DE40_FORWARD_PAPER_EMISSION_FROM_PROMOTED_PLAYBOOKS_20260624_125953")
    p2383c2=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383C2_RISK_NORMALIZATION_REPAIR_20260624_140637")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656")

    s=run(str(dataset),str(p2378),str(p2379),str(p2383c2),str(out))

    required=[
        "de40_p2383d_playbook_source.csv",
        "de40_p2383d_oos_events_all.csv",
        "de40_p2383d_oos_matched_trades_all.csv",
        "de40_p2383d_timeframe_audit.csv",
        "de40_p2383d_playbook_results.csv",
        "de40_p2383d_context_results.csv",
        "de40_p2383d_promoted.csv",
        "de40_p2383d_rejected.csv",
        "summary.json",
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["playbooks_loaded"] > 0
    assert s["oos_events"] > 0

def test_p2383d_summary_gate():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert isinstance(data["p2384_allowed"], bool)
    assert data["certification"] in ["CONTEXTUAL_OOS_PLAYBOOK_PROMOTED","CONTEXTUAL_OOS_PLAYBOOK_NOT_PROMOTED"]
    assert data["matched_oos_trades"] >= 0
