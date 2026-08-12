import json
from pathlib import Path
from tools.p2386_de40_paper_signal_bus_hardening import run

def test_p2386_outputs():
    p2385=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2385_DE40_SURVIVOR_CONTEXT_EXECUTION_FILTER_20260624_174500")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386_DE40_PAPER_SIGNAL_BUS_HARDENING_20260624_175041")

    s=run(str(p2385),str(out))

    required=[
        "mind_de40_paper_signal_bus_p2386.csv",
        "de40_p2386_paper_signals_ready.csv",
        "de40_p2386_quarantine.csv",
        "de40_p2386_blocked_from_p2385.csv",
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
    assert s["ftmo_real_allowed"] is False
    assert s["signals_ready"] > 0

def test_bus_has_no_real_permission():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386_DE40_PAPER_SIGNAL_BUS_HARDENING_20260624_175041")
    bus=(out/"mind_de40_paper_signal_bus_p2386.csv").read_text(encoding="utf-8")
    assert "FORBIDDEN" in bus
    assert "DENIED" in bus
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"] in ["P2386_PAPER_SIGNAL_BUS_CERTIFIED","P2386_PAPER_SIGNAL_BUS_NOT_CERTIFIED"]
