import json
import subprocess
import sys
from pathlib import Path


def test_p1902g_source_validation_engine_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902G_SOURCE_VALIDATION_ENGINE/source_validation_engine.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902G")
    required = [
        "SOURCE_REGISTRY.json",
        "SOURCE_QUALITY_REPORT.json",
        "SOURCE_COVERAGE_MATRIX.json",
        "SOURCE_RANKING.json",
        "DATA_PROVIDER_CATALOG.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902G_SOURCE_VALIDATION_ENGINE"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["provider_count"] > 0
    assert data["approved_for_P1902H"] is True


def test_p1902g_source_ranking_schema():
    ranking = json.loads(Path("_evidence/P1902G/SOURCE_RANKING.json").read_text(encoding="utf-8"))

    assert len(ranking) > 0

    required = {
        "provider",
        "score",
        "grade",
        "scores",
        "jobs",
        "assets",
        "asset_count",
        "timeframes",
        "timeframe_count",
        "asset_classes",
        "rows_missing_supported",
        "approved",
    }

    for row in ranking:
        assert required.issubset(set(row.keys()))
        assert 0 <= row["score"] <= 100
