from pathlib import Path
import json
import subprocess
import sys


def test_p1901_depth_audit_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901_DEPTH_AUDIT/p1901_depth_audit_engine.py"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1901_DEPTH_AUDIT_REPORT.json")
    assert report.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1901_DEPTH_AUDIT"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert "institutional_readiness_score" in data
    assert len(data["modules"]) == 30


def test_no_live_order_terms_inside_p1901():
    root = Path("_institutional/P1901_DEPTH_AUDIT")
    text = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in root.rglob("*.py")
    )

    forbidden_runtime_patterns = [
        "ORDER_SENT" + " = true",
        "REAL_ORDERS" + " = true",
        "FTMO_REAL" + " = true",
        "MT5_REAL" + " = true",
    ]

    for pattern in forbidden_runtime_patterns:
        assert pattern not in text
