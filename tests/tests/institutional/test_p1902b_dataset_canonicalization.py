import json
import subprocess
import sys
from pathlib import Path


def test_p1902b_dataset_canonicalization_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902B_DATASET_CANONICALIZATION/dataset_canonicalization.py"],
        capture_output=True,
        text=True,
        timeout=240,
    )

    assert result.returncode == 0, result.stderr

    summary = Path("_evidence/P1902B/SUMMARY.json")
    assert summary.exists()

    data = json.loads(summary.read_text(encoding="utf-8"))

    assert data["program"] == "P1902B_DATASET_CANONICALIZATION"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["approved_for_P1902C"] is True


def test_p1902b_outputs_exist():
    base = Path("_evidence/P1902B")
    required = [
        "CANONICAL_DATASETS.json",
        "CANONICAL_MEMORYS.json",
        "CANONICAL_FEATURES.json",
        "CANONICAL_SPECIALISTS.json",
        "CANONICAL_BACKTESTS.json",
        "REJECTED_NOISE.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name
