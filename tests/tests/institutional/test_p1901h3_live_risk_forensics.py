import json
import subprocess
import sys
from pathlib import Path


def test_p1901h3_live_risk_forensics_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901H3_LIVE_RISK_FORENSICS/live_risk_forensics.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1901H3/LIVE_RISK_FORENSICS.json")
    assert report.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1901H3_LIVE_RISK_FORENSICS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert "approved_for_P1901I" in data
    assert "blocking_hits" in data
    assert "summary_by_class" in data


def test_p1901h3_report_has_no_schema_break():
    report = Path("_evidence/P1901H3/LIVE_RISK_FORENSICS.json")
    data = json.loads(report.read_text(encoding="utf-8"))

    assert isinstance(data["hits"], list)
    assert isinstance(data["blocking"], list)
    assert isinstance(data["summary_by_class"], dict)
