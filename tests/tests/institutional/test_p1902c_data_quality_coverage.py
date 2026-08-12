import json
import subprocess
import sys
from pathlib import Path


def test_p1902c_data_quality_coverage_audit_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902C_DATA_QUALITY_AND_COVERAGE_AUDIT/data_quality_coverage_audit.py"],
        capture_output=True,
        text=True,
        timeout=240,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1902C/DATA_QUALITY_AND_COVERAGE_AUDIT.json")
    summary = Path("_evidence/P1902C/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1902C_DATA_QUALITY_AND_COVERAGE_AUDIT"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["datasets_audited"] >= 0
    assert data["approved_for_P1902D"] is True


def test_p1902c_summary_schema():
    data = json.loads(Path("_evidence/P1902C/SUMMARY.json").read_text(encoding="utf-8"))

    required = {
        "program",
        "status",
        "datasets_audited",
        "rows_total",
        "avg_ohlcv_schema_score",
        "asset_count",
        "timeframe_count",
        "strong_asset_count",
        "weak_asset_count",
        "quality_flags_total",
        "approved_for_P1902D",
    }

    assert required.issubset(set(data.keys()))
