import json
from pathlib import Path
from tools.p2391_return_to_edge_research import run

def test_p2391_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    baseline=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2390_DE40_PAPER_ONLY_TEST_SUITE_20260624_215627")
    lock=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK_20260624_215039")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2391_RETURN_TO_EDGE_RESEARCH_20260624_220417")
    s=run(str(dataset),str(baseline),str(lock),str(out))

    required=[
        "de40_p2391_edge_candidates_all.csv",
        "de40_p2391_edge_promoted.csv",
        "de40_p2391_edge_observed.csv",
        "de40_p2391_edge_rejected.csv",
        "de40_p2391_promoted_detail_events.csv",
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

def test_baseline_not_modified():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2391_RETURN_TO_EDGE_RESEARCH_20260624_220417")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["baseline_metrics"]["pf"] == 1.543464
    assert data["certification"] in ["P2391_EDGE_RESEARCH_PROMOTED","P2391_EDGE_RESEARCH_NO_SUPERIOR_EDGE"]
