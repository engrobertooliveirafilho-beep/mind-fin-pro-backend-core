import json
from pathlib import Path
from tools.p2384a_transition_gate_context_fidelity_repair import run

def test_p2384a_outputs():
    p2383d=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656")
    p2384=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE_20260624_171307")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384A_TRANSITION_PROMOTION_GATE_AND_CONTEXT_FIDELITY_REPAIR_20260624_173034")

    s=run(str(p2383d),str(p2384),str(out))

    required=[
        "de40_p2384a_cycle_promoted.csv",
        "de40_p2384a_transition_promoted.csv",
        "de40_p2384a_context_fidelity_all.csv",
        "de40_p2384a_high_fidelity_matches.csv",
        "de40_p2384a_rejected_fidelity_matches.csv",
        "de40_p2384a_final_promoted_contexts.csv",
        "de40_p2384a_p2383d_seed.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert isinstance(s["p2385_allowed"], bool)

def test_p2384a_transition_gate_detects_passed():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384A_TRANSITION_PROMOTION_GATE_AND_CONTEXT_FIDELITY_REPAIR_20260624_173034")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))

    assert data["transition_promoted"] >= 1
    assert data["certification"] in ["P2384A_PROMOTED","P2384A_NOT_PROMOTED"]
