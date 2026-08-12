import json
from pathlib import Path
from tools.p2388b_runtime_reachability_orphan_audit import run

def test_reachability_outputs():
    root=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core")
    evidence=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence")
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2388B_TRADER_RUNTIME_REACHABILITY_ORPHAN_AUDIT_20260624_181819")
    s=run(str(root),str(evidence),str(out))

    required=[
        "runtime_files.csv",
        "runtime_import_edges.csv",
        "runtime_textual_refs.csv",
        "runtime_defs.csv",
        "runtime_reachability.csv",
        "runtime_orphans_critical.csv",
        "runtime_dangerous_patterns.csv",
        "evidence_summary_audit.csv",
        "evidence_broken_safety.csv",
        "runtime_reachability.dot",
        "summary.json",
    ]

    for f in required:
        p=out/f
        assert p.exists(), f
        assert p.stat().st_size>0, f

    assert s["mode"]=="PAPER_ONLY"
    assert s["real_orders"]=="FORBIDDEN"
    assert s["ftmo_real"]=="FORBIDDEN"
    assert s["python_files"] > 0
    assert s["modules"] > 0

def test_summary_has_decision():
    out=Path(r"C:\\Users\\MindFin\\Desktop\\mind-fin-pro-backend-core_evidence\\P2388B_TRADER_RUNTIME_REACHABILITY_ORPHAN_AUDIT_20260624_181819")
    data=json.loads((out/"summary.json").read_text(encoding="utf-8"))
    assert data["certification"] in [
        "P2388B_RUNTIME_REACHABILITY_CERTIFIED",
        "P2388B_RUNTIME_REACHABILITY_REQUIRES_REPAIR"
    ]
    assert data["next_required"] in [
        "P2389_DE40_PAPER_FORWARD_GOVERNANCE_LOCK",
        "P2388C_RUNTIME_ORPHAN_REPAIR"
    ]
