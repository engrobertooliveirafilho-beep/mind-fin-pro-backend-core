import json
from pathlib import Path
from tools.p2386b_signal_bus_schema_repair import run

def test_p2386b_outputs():
    p2385=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER_20260624_174500")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386B_SIGNAL_BUS_SCHEMA_REPAIR_20260624_175427")
    s=run(str(p2385),str(out))

    required=[
        "mind_de40_paper_signal_bus_p2386b.csv",
        "de40_p2386b_paper_signals_ready.csv",
        "de40_p2386b_quarantine.csv",
        "de40_p2386b_blocked_preserved.csv",
        "summary.json"
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["signals_ready"] == s["input_allowed"]
    assert s["quarantine"] == 0
    assert s["real_execution_allowed"] is False

def test_bus_denies_real():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386B_SIGNAL_BUS_SCHEMA_REPAIR_20260624_175427")
    txt=(out/"mind_de40_paper_signal_bus_p2386b.csv").read_text(encoding="utf-8")
    assert "PAPER_SIGNAL_READY" in txt
    assert "FORBIDDEN" in txt
    assert "DENIED" in txt
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"]=="P2386B_SIGNAL_BUS_CERTIFIED"
