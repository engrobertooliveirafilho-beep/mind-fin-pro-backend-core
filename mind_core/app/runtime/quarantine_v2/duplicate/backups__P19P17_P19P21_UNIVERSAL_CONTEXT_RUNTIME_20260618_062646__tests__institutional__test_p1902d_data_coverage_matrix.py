import json
import subprocess
import sys
from pathlib import Path


def test_p1902d_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902D_DATA_COVERAGE_MATRIX/data_coverage_matrix.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1902D/DATA_COVERAGE_MATRIX.json")
    summary = Path("_evidence/P1902D/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(summary.read_text())

    assert data["program"] == "P1902D_DATA_COVERAGE_MATRIX"
    assert data["status"] == "PASS"
    assert data["approved_for_P1902E"] is True
