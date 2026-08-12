import json
import subprocess
import sys
from pathlib import Path


def test_p1901i_module_registry_reconstruction_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901I_MODULE_REGISTRY_RECONSTRUCTION/module_registry_reconstruction.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    master = Path("_evidence/P1901I/MASTER_REGISTRY.json")
    summary = Path("_evidence/P1901I/SUMMARY.json")

    assert master.exists()
    assert summary.exists()

    data = json.loads(master.read_text(encoding="utf-8"))

    assert data["program"] == "P1901I_MODULE_REGISTRY_RECONSTRUCTION"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["capability_total"] > 0
    assert len(data["capabilities"]) == data["capability_total"]
    assert data["approved_for_P1901J"] is True


def test_p1901i_capability_schema_integrity():
    data = json.loads(Path("_evidence/P1901I/MASTER_REGISTRY.json").read_text(encoding="utf-8"))

    required = {
        "capability_id",
        "category",
        "type",
        "file",
        "owner_module",
        "functions",
        "classes",
        "lines",
        "dependencies",
        "institutional_score",
        "maturity",
        "status",
    }

    for cap in data["capabilities"]:
        assert required.issubset(set(cap.keys()))
        assert isinstance(cap["dependencies"], list)
        assert 0 <= cap["institutional_score"] <= 100
