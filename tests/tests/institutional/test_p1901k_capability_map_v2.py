import json
import subprocess
import sys
from pathlib import Path


def test_p1901k_capability_map_v2_runs():
    result = subprocess.run(
        [sys.executable, "_institutional/P1901K_CAPABILITY_MAP_V2/capability_map_v2.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, result.stderr

    report = Path("_evidence/P1901K/CAPABILITY_MAP_V2.json")
    summary = Path("_evidence/P1901K/SUMMARY.json")

    assert report.exists()
    assert summary.exists()

    data = json.loads(report.read_text(encoding="utf-8"))

    assert data["program"] == "P1901K_CAPABILITY_MAP_V2"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["order_sent"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["ftmo_real"] == "FORBIDDEN"
    assert data["mt5_real"] == "FORBIDDEN"
    assert data["capability_total"] > 0
    assert len(data["capabilities"]) == data["capability_total"]
    assert data["approved_for_P1901L"] is True


def test_p1901k_upgrade_queue_schema():
    data = json.loads(Path("_evidence/P1901K/CAPABILITY_MAP_V2.json").read_text(encoding="utf-8"))

    required = {
        "capability_id",
        "file",
        "owner_module",
        "category",
        "type",
        "maturity",
        "institutional_score",
        "target_score",
        "gap_to_target",
        "priority",
        "expansion_recommendations",
    }

    assert len(data["top_50_upgrade_queue"]) > 0

    for item in data["top_50_upgrade_queue"]:
        assert required.issubset(set(item.keys()))
        assert isinstance(item["expansion_recommendations"], list)
