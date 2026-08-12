import json
from pathlib import Path
from tools.p2387_de40_mt5_paper_bridge_validation import run

def test_p2387_outputs():
    p2386b=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386B_SIGNAL_BUS_SCHEMA_REPAIR_20260624_175427")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION_20260624_175907")
    s=run(str(p2386b),str(out))

    required=[
        "mind_de40_mt5_paper_bridge_p2387.csv",
        "de40_p2387_validated_signals.csv",
        "de40_p2387_invalid_signals.csv",
        "de40_p2387_mt5_bridge_ready.csv",
        "mt5_common_files_simulated/mind_de40_mt5_paper_bridge_p2387.csv",
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
    assert s["invalid_signals"] == 0
    assert s["bridge_ready"] == s["input_signals"]

def test_bridge_denies_real():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION_20260624_175907")
    txt=(out/"mind_de40_mt5_paper_bridge_p2387.csv").read_text(encoding="utf-8")
    assert "DENIED" in txt
    assert "FORBIDDEN" in txt
    assert "PAPER_ONLY_SIMULATION" in txt
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"]=="P2387_MT5_PAPER_BRIDGE_CERTIFIED"
