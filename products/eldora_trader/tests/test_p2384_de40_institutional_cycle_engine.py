import json
from pathlib import Path
from tools.p2384_de40_institutional_cycle_engine import run

def test_p2384_outputs():
    dataset=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2363C_VALIDATE_DE40_5Y_DATASET_DOTNET_20260623_180821")
    p2383d=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2383D_EXACT_PLAYBOOK_TO_RAW_CANDLE_VALIDATOR_20260624_141656")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE_20260624_171307")
    s=run(str(dataset),str(p2383d),str(out))

    required=[
        "de40_cycle_events.csv",
        "de40_cycle_survivor_matches.csv",
        "de40_cycle_playbook_results.csv",
        "de40_cycle_transition_results.csv",
        "de40_cycle_transition_matrix.csv",
        "de40_cycle_promoted.csv",
        "de40_cycle_rejected.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["events"]>0

def test_p2384_gate():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2384_DE40_INSTITUTIONAL_CYCLE_ENGINE_20260624_171307")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert isinstance(data["p2385_allowed"], bool)
    assert data["certification"] in ["CYCLE_CONTEXT_PROMOTED","CYCLE_CONTEXT_NOT_PROMOTED"]
