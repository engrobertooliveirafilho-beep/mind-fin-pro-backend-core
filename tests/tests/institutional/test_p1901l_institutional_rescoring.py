import json
import subprocess
import sys
from pathlib import Path


def test_p1901l_institutional_rescoring_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901L_INSTITUTIONAL_RESCORING/institutional_rescoring.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1901L/INSTITUTIONAL_RESCORING.json")
    summary = Path("_evidence/P1901L/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1901L_INSTITUTIONAL_RESCORING"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["capability_total"] > 0
    assert data["final_diagnosis"]["approved_for_P1902"] is True


def test_p1901l_dimension_report_integrity():
    data = json.loads(Path("_evidence/P1901L/INSTITUTIONAL_RESCORING.json").read_text(encoding="utf-8"))

    assert isinstance(data["dimension_report"], dict)
    assert len(data["dimension_report"]) > 0

    for _, item in data["dimension_report"].items():
        assert "score" in item
        assert "classification" in item
        assert "capabilities" in item
        assert 0 <= item["score"] <= 100
