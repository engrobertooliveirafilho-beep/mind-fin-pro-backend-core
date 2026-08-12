import json
import subprocess
import sys
from pathlib import Path

def test_p2005_package():
    result = subprocess.run(
        [sys.executable, "_institutional/P2005A_J_REAL_MEMORY_CONSTRUCTION_PACKAGE/real_memory_construction_package.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2005A_J/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2005J_REAL_MEMORY_CONSTRUCTION_CERTIFICATION"
    assert data["status"] == "PASS"
    assert data["target_memory_count"] == 100000
    assert data["memories_created"] == 0
    assert data["write_enabled"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2006"] is True
