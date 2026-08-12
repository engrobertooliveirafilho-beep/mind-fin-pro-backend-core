import json
import subprocess
import sys
from pathlib import Path

def test_p2001d_zero_write_sample_builder():
    result = subprocess.run(
        [sys.executable, "_institutional/P2001D_ZERO_WRITE_SAMPLE_BUILDER/zero_write_sample_builder.py"],
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0

    data = json.loads(Path("_evidence/P2001D/SUMMARY.json").read_text(encoding="utf-8"))

    assert data["program"] == "P2001D_ZERO_WRITE_SAMPLE_BUILDER"
    assert data["status"] == "PASS"
    assert data["mode"] == "RESEARCH_ONLY"
    assert data["download_executed"] is False
    assert data["files_written"] is False
    assert data["real_orders"] == "FORBIDDEN"
    assert data["approved_for_P2001E"] is True
