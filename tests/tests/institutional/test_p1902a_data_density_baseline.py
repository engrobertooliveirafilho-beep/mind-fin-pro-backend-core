import json
import subprocess
import sys
from pathlib import Path


def test_p1902a_data_density_baseline_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902A_DATA_DENSITY_BASELINE/data_density_baseline.py"],
        capture_output=True,
        text=True,
        timeout=240,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1902A/DATA_DENSITY_BASELINE.json")
    assert report.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1902A_DATA_DENSITY_BASELINE"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["files_scanned"] >= 0
    assert data["approved_for_P1902B"] is True


def test_p1902a_registries_exist():
    base = Path("_evidence/P1902A")
    required = [
        "DATASET_REGISTRY.json",
        "MEMORY_REGISTRY.json",
        "FEATURE_REGISTRY.json",
        "SPECIALIST_REGISTRY.json",
        "BACKTEST_REGISTRY.json",
        "DATA_DENSITY_BASELINE.json",
    ]

    for name in required:
        assert (base / name).exists()
