import json
import subprocess
import sys
from pathlib import Path


def test_p1902d2_unified_coverage_matrix_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902D2_UNIFIED_COVERAGE_MATRIX/unified_coverage_matrix.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1902D2/UNIFIED_COVERAGE_MATRIX.json")
    summary = Path("_evidence/P1902D2/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(summary.read_text(encoding="utf-8"))

    assert data["program"] == "P1902D2_UNIFIED_COVERAGE_MATRIX"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["approved_for_P1902F"] is True
    assert data["asset_count"] >= 6


def test_p1902d2_asset_schema():
    data = json.loads(Path("_evidence/P1902D2/UNIFIED_COVERAGE_MATRIX.json").read_text(encoding="utf-8"))

    assert isinstance(data["assets"], list)
    assert len(data["assets"]) > 0

    required = {"asset", "composite_coverage_score", "priority", "layers"}

    for asset in data["assets"]:
        assert required.issubset(set(asset.keys()))
        assert "dataset" in asset["layers"]
        assert "memory" in asset["layers"]
        assert "feature" in asset["layers"]
        assert "specialist" in asset["layers"]
        assert "backtest" in asset["layers"]
