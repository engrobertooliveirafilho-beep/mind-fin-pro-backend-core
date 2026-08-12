import json
import subprocess
import sys
from pathlib import Path


def test_p1902h_mass_normalization_plan_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1902H_MASS_NORMALIZATION_PLAN/mass_normalization_plan.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    base = Path("_evidence/P1902H")
    required = [
        "MASS_NORMALIZATION_PLAN.json",
        "NORMALIZATION_MANIFESTS.json",
        "SUMMARY.json",
    ]

    for name in required:
        assert (base / name).exists(), name

    data = json.loads((base / "SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P1902H_MASS_NORMALIZATION_PLAN"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["normalization_batches"] > 0
    assert data["approved_for_P1902I"] is True
