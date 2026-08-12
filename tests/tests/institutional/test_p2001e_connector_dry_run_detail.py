import json
import subprocess
import sys
from pathlib import Path

def test_p2001e_connector_dry_run_detail():
    result = subprocess.run(
        [sys.executable, "_institutional/P2001E_CONNECTOR_DRY_RUN_DETAIL/connector_dry_run_detail.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2001E/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2001E_CONNECTOR_DRY_RUN_DETAIL"
    assert data["status"] == "PASS"
    assert data["dry_run_count"] > 0
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001F"] is True
