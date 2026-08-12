import json
from pathlib import Path
from tools.p2385_de40_survivor_context_execution_filter import run

def test_p2385_outputs():
    p2383d=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656")
    p2384a=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384A_TRANSITION_PROMOTION_GATE_AND_CONTEXT_FIDELITY_REPAIR_20260624_173034")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER_20260624_174500")

    s=run(str(p2383d),str(p2384a),str(out))

    required=[
        "de40_p2385_execution_filter_all.csv",
        "de40_p2385_allowed_paper.csv",
        "de40_p2385_blocked.csv",
        "de40_p2385_block_reasons.csv",
        "de40_p2385_allowed_transitions.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["real_execution_allowed"] is False

def test_no_real_execution_allowed():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER_20260624_174500")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["real_execution_allowed"] is False
    assert data["certification"] in ["P2385_EXECUTION_FILTER_CERTIFIED","P2385_EXECUTION_FILTER_NOT_CERTIFIED"]
