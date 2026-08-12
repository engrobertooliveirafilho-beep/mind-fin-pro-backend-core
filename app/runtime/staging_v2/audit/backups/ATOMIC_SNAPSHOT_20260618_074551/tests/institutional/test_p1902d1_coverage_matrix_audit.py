import json
import subprocess
import sys
from pathlib import Path


def test_p1902d1_coverage_matrix_audit_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902D1_COVERAGE_MATRIX_AUDIT/coverage_matrix_audit.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1902D1/COVERAGE_MATRIX_AUDIT.json")
    summary = Path("_evidence/P1902D1/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(summary.read_text(encoding="utf-8"))

    assert data["program"] == "P1902D1_COVERAGE_MATRIX_AUDIT"
    assert data["status"] == "PASS"
    assert "inconsistency_detected" in data
    assert "approved_for_P1902F" in data
