import json
from pathlib import Path
from tools.p2388_de40_paper_forward_monitor import run

def test_p2388_outputs():
    p2387=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2387_DE40_MT5_PAPER_BRIDGE_VALIDATION_20260624_175907")
    p2386b=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2386B_SIGNAL_BUS_SCHEMA_REPAIR_20260624_175427")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2388_DE40_PAPER_FORWARD_MONITOR_20260624_180202")
    s=run(str(p2387),str(p2386b),str(out))

    required=[
        "mind_de40_paper_monitor_bus.csv",
        "de40_forward_active.csv",
        "de40_forward_closed.csv",
        "de40_forward_expired.csv",
        "de40_forward_statistics.csv",
        "de40_forward_equity_curve.csv",
        "de40_forward_learning_events.csv",
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
    assert s["input_bridge_signals"] == s["closed"]

def test_forward_stats_positive_cert_gate():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2388_DE40_PAPER_FORWARD_MONITOR_20260624_180202")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["statistics"]["samples"] > 0
    assert data["certification"] in ["P2388_PAPER_FORWARD_MONITOR_CERTIFIED","P2388_PAPER_FORWARD_MONITOR_NOT_CERTIFIED"]
    txt=(out/"mind_de40_paper_monitor_bus.csv").read_text(encoding="utf-8")
    assert "PAPER_FORWARD_MONITOR_ONLY_NOT_REAL_ORDER" in txt
    assert "FORBIDDEN" in txt
