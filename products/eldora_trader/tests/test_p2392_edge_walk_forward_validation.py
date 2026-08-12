import json
from pathlib import Path
from tools.p2392_edge_walk_forward_validation import run

def test_p2392_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    p2391=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2391_RETURN_TO_EDGE_RESEARCH_20260624_220417")
    lock=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342")

    s=run(str(dataset),str(p2391),str(lock),str(out))

    required=[
        "de40_edge_walkforward_results.csv",
        "de40_edge_promoted.csv",
        "de40_edge_observed.csv",
        "de40_edge_rejected.csv",
        "de40_edge_stability.csv",
        "de40_edge_walkforward_detail.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["paper_stack_modified"] is False
    assert s["real_execution_allowed"] is False

def test_p2392_decision_valid():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2392_EDGE_WALK_FORWARD_VALIDATION_20260624_221342")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"] in [
        "P2392_EDGE_WALK_FORWARD_PROMOTED",
        "P2392_EDGE_WALK_FORWARD_NO_PROMOTION"
    ]
    assert data["input_candidates"] > 0
