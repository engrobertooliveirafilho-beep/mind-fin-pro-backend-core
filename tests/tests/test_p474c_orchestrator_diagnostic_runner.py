import json
import subprocess
import sys
from pathlib import Path


def test_p474c_runner_executes():
    out_path = Path("_evidence/p474c_test_runner_output.json")
    cmd = [
        sys.executable,
        "tools/run_capability_orchestrator_diagnostic.py",
        "--user",
        "whatsapp:+5519996166906",
        "--message",
        "Roberto matemática",
        "--out",
        str(out_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    assert result.returncode == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))

    assert "diagnostic" in data
    assert "summary" in data
    assert data["summary"]["used"] >= 1
